__author__ = 'guilherme'

import os
import os.path
import tempfile
import time
import shutil
import subprocess
import uuid

import py2neo.cypher.error.transaction
from py2neo.packages.httpstream import http
from tapirus.core import errors
from tapirus.core.db import neo4j
from tapirus.model.constants import *
from tapirus.model.store import is_valid_schema, is_acceptable_data_type
from tapirus.utils import io
from tapirus.utils.logger import Logger


NEO4J_SHELL = "neo4j-shell"
PATHS = ["/usr/local/bin"]


class Neo4jEventHandler(object):

    def __init__(self):
        pass

    def handle(self, entry):

        events = self.transform(entry)

        return events

    def handle_events(self, entries):

        size = 500
        c = 0

        events = []

        for entity in entries:

            events.extend(self.handle(entity))

            if c % size == 0 and c > 0 and events:

                start = time.time()*1000
                self.execute_batch_transactions(events)
                end = time.time()*1000

                Logger.info("\tImport to Neo4j: {0:0.00f}ms, for {1} queries".format(end-start, len(events)))
                del events[:]

            c += 1

        if events:

            start = time.time()*1000
            self.execute_batch_transactions(events)
            end = time.time()*1000

            Logger.info("\tImport to Neo4j: {0:0.00f}ms, for {1} queries".format(end-start, len(events)))

            del events[:]


    @classmethod
    def instance(cls):

        return cls()

    @classmethod
    def transform(cls, data):

        dt = data["datetime"]

        if is_valid_schema(data) is False:
            return []

        queries = []

        if data[SCHEMA_KEY_TENANT_ID] in ("bukalapak",):
            return []

        # session
        statements = ["MERGE (n :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
            SESSION_LABEL=LABEL_SESSION,
            STORE_ID=data[SCHEMA_KEY_TENANT_ID]
        )]

        params = [neo4j.Parameter("id", data[SCHEMA_KEY_SESSION_ID])]

        queries.append(neo4j.Query(''.join(statements), params))

        #user
        if SCHEMA_KEY_USER in data:
            #todo: if user is not given, use anonymous user id?

            statements = ["MERGE (n :`{USER_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
                USER_LABEL=LABEL_USER,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID]
            )]

            params = [neo4j.Parameter("id", data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID])]

            for k, v in data[SCHEMA_KEY_USER].items():

                if k != SCHEMA_KEY_USER_ID and is_acceptable_data_type(v):
                    params.append(neo4j.Parameter(k, v))
                    statements.append("\nSET n.{0} = {{ {0} }}".format(
                        k
                    ))

            queries.append(neo4j.Query(''.join(statements), params))

            #(session)-[r]-(user)

            template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                       "\nMERGE (i :`{USER_LABEL}` :`{STORE_ID}` {{id: {{user_id}} }})" \
                       "\nMERGE (s)-[r :`{REL}`]->(i)"

            statements = [template.format(
                SESSION_LABEL=LABEL_SESSION,
                USER_LABEL=LABEL_USER,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                REL=REL_SESSION_TO_USER
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("user_id", data[SCHEMA_KEY_USER][SCHEMA_KEY_USER_ID]),
                      neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

            queries.append(neo4j.Query(''.join(statements), params))

        #agent
        if SCHEMA_KEY_AGENT_ID in data:
            statements = ["MERGE (n :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{id}} }})".format(
                AGENT_LABEL=LABEL_AGENT,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID]
            )]

            params = [neo4j.Parameter("id", data[SCHEMA_KEY_AGENT_ID])]

            queries.append(neo4j.Query(''.join(statements), params))

            #(session)-[r]-(agent)
            template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                       "\nMERGE (i :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{agent_id}} }})" \
                       "\nMERGE (s)-[r :`{REL}`]->(i)"
            #"(i :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{agent_id}} }})"

            statements = [template.format(
                SESSION_LABEL=LABEL_SESSION,
                AGENT_LABEL=LABEL_AGENT,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                REL=REL_SESSION_TO_AGENT
            )]

            params = [neo4j.Parameter("datetime", dt),
                      neo4j.Parameter("agent_id", data[SCHEMA_KEY_AGENT_ID]),
                      neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

            queries.append(neo4j.Query(''.join(statements), params))

        # actions
        if data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_VIEW:

            # collect items
            for item in data[SCHEMA_KEY_ITEMS]:

                template = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

                statements = [template.format(
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=data[SCHEMA_KEY_TENANT_ID]
                )]

                params = [neo4j.Parameter("id", item[SCHEMA_KEY_ITEM_ID])]

                for k, v in item.items():

                    if k != SCHEMA_KEY_ITEM_ID and is_acceptable_data_type(v):
                        params.append(neo4j.Parameter(k, v))
                        statements.append("\nSET n.{0} = {{ {0} }}".format(
                            k
                        ))

                queries.append(neo4j.Query(''.join(statements), params))

                # (item)-[r]-(location)

                if SCHEMA_KEY_LOCATION in item:

                    if SCHEMA_KEY_COUNTRY in item[SCHEMA_KEY_LOCATION]:
                        template = "MERGE (l:`{LOCATION_LABEL}` :`{LOCATION_COUNTRY}` :`{STORE_ID}` {{name: {{name}} }})" \
                                   "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                                   "\nMERGE (i)-[:`{REL}`]->(l)"

                        statements = [template.format(
                            LOCATION_LABEL=LABEL_LOCATION,
                            LOCATION_COUNTRY=LABEL_LOCATION_COUNTRY,
                            ITEM_LABEL=LABEL_ITEM,
                            STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                            REL=REL_ITEM_LOCATION
                        )]

                        params = [neo4j.Parameter("name", item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_COUNTRY]),
                                  neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID])]

                        queries.append(neo4j.Query(''.join(statements), params))

                    if SCHEMA_KEY_CITY in item[SCHEMA_KEY_LOCATION]:
                        template = "MERGE (l:`{LOCATION_LABEL}` :`{LOCATION_CITY}` :`{STORE_ID}` {{name: {{name}} }})" \
                                   "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                                   "\nMERGE (i)-[:`{REL}`]->(l)"

                        statements = [template.format(
                            LOCATION_LABEL=LABEL_LOCATION,
                            LOCATION_CITY=LABEL_LOCATION_CITY,
                            ITEM_LABEL=LABEL_ITEM,
                            STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                            REL=REL_ITEM_LOCATION
                        )]

                        params = [neo4j.Parameter("name", item[SCHEMA_KEY_LOCATION][SCHEMA_KEY_CITY]),
                                  neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID])]

                        queries.append(neo4j.Query(''.join(statements), params))

                # (item)-[r]-(session)

                template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                           "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                           "\nMERGE (s)-[r :`{REL}`]->(i)"

                statements = [template.format(
                    SESSION_LABEL=LABEL_SESSION,
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                    REL=REL_ACTION_TYPE_VIEW
                )]

                params = [neo4j.Parameter("datetime", dt),
                          neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID]),
                          neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

                statements.append("\nSET r.{0} = {{ {0} }}".format(
                    "datetime"
                ))

                queries.append(neo4j.Query(''.join(statements), params))

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_ADD_TO_CART:

            # collect items
            for item in data[SCHEMA_KEY_ITEMS]:
                template = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

                statements = [template.format(
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=data[SCHEMA_KEY_TENANT_ID]
                )]

                params = [neo4j.Parameter("id", item[SCHEMA_KEY_ITEM_ID])]

                queries.append(neo4j.Query(''.join(statements), params))

                # (item)-[r]-(session)

                template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                           "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                           "\nMERGE (s)-[r :`{REL}`]->(i)"
                # "(i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})"

                statements = [template.format(
                    SESSION_LABEL=LABEL_SESSION,
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                    REL=REL_ACTION_TYPE_ADD_TO_CART
                )]

                params = [neo4j.Parameter("datetime", dt),
                          neo4j.Parameter("qty", item[SCHEMA_KEY_QUANTITY]),
                          neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID]),
                          neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

                statements.append("\nSET r.{0} = {{ {0} }}".format(
                    "datetime"
                ))

                statements.append("\nSET r.{0} = {{ {0} }}".format(
                    "qty"
                ))

                queries.append(neo4j.Query(''.join(statements), params))

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_BUY:

            # collect items
            for item in data[SCHEMA_KEY_ITEMS]:
                template = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

                statements = [template.format(
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=data[SCHEMA_KEY_TENANT_ID]
                )]

                params = [neo4j.Parameter("id", item[SCHEMA_KEY_ITEM_ID])]

                queries.append(neo4j.Query(''.join(statements), params))

                # (item)-[r]-(session)

                template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                           "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                           "\nMERGE (s)-[r :`{REL}`]->(i)"

                statements = [template.format(
                    SESSION_LABEL=LABEL_SESSION,
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                    REL=REL_ACTION_TYPE_BUY
                )]

                params = [neo4j.Parameter("datetime", dt),
                          neo4j.Parameter("qty", item[SCHEMA_KEY_QUANTITY]),
                          neo4j.Parameter("sub_total", item[SCHEMA_KEY_SUBTOTAL]),
                          neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID]),
                          neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

                statements.append("\nSET r.{0} = {{ {0} }}".format(
                    "datetime"
                ))

                statements.append("\nSET r.{0} = {{ {0} }}".format(
                    "qty"
                ))

                statements.append("\nSET r.{0} = {{ {0} }}".format(
                    "sub_total"
                ))

                queries.append(neo4j.Query(''.join(statements), params))

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_STARTED_CHECKOUT:

            # collect items
            for item in data[SCHEMA_KEY_ITEMS]:
                template = "MERGE (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

                statements = [template.format(
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=data[SCHEMA_KEY_TENANT_ID]
                )]

                params = [neo4j.Parameter("id", item[SCHEMA_KEY_ITEM_ID])]

                queries.append(neo4j.Query(''.join(statements), params))

                # (item)-[r]-(session)

                template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                           "\nMERGE (i :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                           "\nMERGE (s)-[r :`{REL}`]->(i)"

                statements = [template.format(
                    SESSION_LABEL=LABEL_SESSION,
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                    REL=REL_ACTION_TYPE_STARTED_CHECKOUT
                )]

                params = [neo4j.Parameter("datetime", dt),
                          neo4j.Parameter("item_id", item[SCHEMA_KEY_ITEM_ID]),
                          neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID])]

                statements.append("\nSET r.{0} = {{ {0} }}".format(
                    "datetime"
                ))

                queries.append(neo4j.Query(''.join(statements), params))

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_SEARCH:

            template = "MERGE (s :`{SESSION_LABEL}` :`{STORE_ID}` {{ id: {{session_id}} }})" \
                       "\nMERGE (n :`{SEARCH_LABEL}` :`{STORE_ID}` {{ keywords: {{keywords}} }})" \
                       "\nMERGE (s)-[r :`{REL}`]->(n)"

            #collect items
            statements = [template.format(
                SEARCH_LABEL=LABEL_SEARCH,
                SESSION_LABEL=LABEL_SESSION,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID],
                REL=REL_ACTION_TYPE_SEARCH
            )]

            params = [neo4j.Parameter("keywords", data[SCHEMA_KEY_ACTION][SCHEMA_KEY_KEYWORDS]),
                      neo4j.Parameter("session_id", data[SCHEMA_KEY_SESSION_ID]),
                      neo4j.Parameter("datetime", dt)]

            queries.append(neo4j.Query(''.join(statements), params))

            for k, v in data[SCHEMA_KEY_ACTION].items():

                if k != SCHEMA_KEY_KEYWORDS and is_acceptable_data_type(v):
                    params.append(neo4j.Parameter(k, v))
                    statements.append("\nSET n.{0} = {{ {0} }}".format(
                        k
                    ))

            statements.append("\nSET r.{0} = {{ {0} }}".format(
                "datetime"
            ))

            queries.append(neo4j.Query(''.join(statements), params))

        elif data[SCHEMA_KEY_ACTION][SCHEMA_KEY_NAME].upper() == REL_ACTION_TYPE_CHECK_DELETE_ITEM:

            template = "MATCH (n :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})" \
                       "\nOPTIONAL MATCH (n)-[r]-(x)" \
                       "\nDELETE r, n"

            statements = [template.format(
                ITEM_LABEL=LABEL_ITEM,
                STORE_ID=data[SCHEMA_KEY_TENANT_ID]
            )]

            params = [neo4j.Parameter("id", data[SCHEMA_KEY_ITEM_ID])]

            queries.append(neo4j.Query(''.join(statements), params))

        return queries

    @classmethod
    def execute_batch_transactions(cls, queries):

        try:

            neo4j.run_batch_query(queries, commit=True, timeout=60)

        except py2neo.cypher.error.transaction.DeadlockDetected as exc:

            Logger.error(exc)

            nap_time = 10

            Logger.info("Sleeping for {0}s".format(nap_time))
            time.sleep(nap_time)

            raise errors.ProcessFailure("Neo4j deadlock")

        except http.SocketError as exc:

            Logger.error(exc)

            raise errors.ProcessFailure("Socket timeout")

    @classmethod
    def neo4j_shell_import(cls, queries):

        if os.name == 'posix':
            for path in PATHS:
                os.environ["PATH"] = ''.join([os.environ["PATH"], os.pathsep, path])

        neo4j_shell_path = shutil.which(NEO4J_SHELL)

        if not neo4j_shell_path:
            raise ChildProcessError("Couldn't find {0} executable path".format(NEO4J_SHELL))

        # use random uuid for file name. avoid race conditions
        file_name = str(uuid.uuid4())
        tmp_folder = tempfile.gettempdir()
        file_path = os.path.join(tmp_folder, file_name)

        Logger.info("Writing queries to file `{0}`".format(file_path))

        with open(file_path, "w", encoding="UTF-8") as f:

            for query in queries:

                for k, v in query.parameters.items():
                    if type(v) is str:
                        value = repr(v).strip("'")
                        s = u"\nexport {0}={1}\n".format(k, value)
                    else:
                        s = u"\nexport {0}={1}\n".format(k, v)
                    f.write(s)

                s = u"{0};\n".format(query.query)
                f.write(s)

        p = subprocess.Popen([neo4j_shell_path, "-file", file_path], stdout=subprocess.PIPE, shell=False)

        output, err = p.communicate()

        io.delete_file(file_path)

        if p.returncode == 1:

            msg = "Error importing data via {0}:\n\t{1}".format(NEO4J_SHELL, output)
            Logger.error(msg)

            raise ChildProcessError(msg)

        elif p.returncode == 0:

            Logger.info("Successfully executed [{0}] queries".format(len(queries)))