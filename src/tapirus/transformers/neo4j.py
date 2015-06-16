import time

from py2neo.packages.httpstream import http
import py2neo.error
import py2neo.cypher
import py2neo.cypher.error.transaction

from tapirus.core.db import neo4j
from tapirus.model.constants import *
from tapirus.model.store import Session, Agent, User, Item, Action, is_acceptable_data_type
from tapirus.utils.logger import Logger
from tapirus.core import errors


NEO4J_SHELL = "neo4j-shell"
PATHS = ["/usr/local/bin"]


class Neo4jDataHandler(object):

    def __init__(self):
        pass

    @classmethod
    def transform(cls, session, agent, user, items, actions):

        assert isinstance(session, Session)
        assert isinstance(agent, Agent)
        assert isinstance(user, User)
        assert type(items) is set
        assert type(actions) is list

        queries = []

        # TODO: follow a signature: template, statements
        # TODO: ID as label
        # Session
        template = "MERGE (session :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

        statements = [template.format(
            SESSION_LABEL=LABEL_SESSION,
            STORE_ID=session.tenant
        )]

        params = [neo4j.Parameter("id", session.id)]

        queries.append(neo4j.Query(''.join(statements), params))

        # User
        template = "MERGE (user :`{USER_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

        statements = [template.format(
            USER_LABEL=LABEL_USER,
            STORE_ID=session.tenant
        )]

        params = [neo4j.Parameter("id", user.id)]

        for k, v in user.fields.items():

            if is_acceptable_data_type(v):
                params.append(neo4j.Parameter(k, v))
                statements.append(
                    "\nSET user.{0} = {{ {0} }}".format(
                        k
                    )
                )

        queries.append(neo4j.Query(''.join(statements), params))

        # (session)-[r]-(user)

        template = "MERGE (session :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                   "\nMERGE (user :`{USER_LABEL}` :`{STORE_ID}` {{id: {{user_id}} }})" \
                   "\nMERGE (session)-[r :`{REL}`]->(user)"

        statements = [template.format(
            SESSION_LABEL=LABEL_SESSION,
            USER_LABEL=LABEL_USER,
            STORE_ID=session.tenant,
            REL=REL_SESSION_TO_USER
        )]

        params = [neo4j.Parameter("user_id", user.id),
                  neo4j.Parameter("session_id", session.id)]

        queries.append(neo4j.Query(''.join(statements), params))

        # Agent
        template = "MERGE (agent :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

        statements = [template.format(
            AGENT_LABEL=LABEL_AGENT,
            STORE_ID=agent.tenant
        )]

        params = [neo4j.Parameter("id", agent.id)]

        queries.append(neo4j.Query(''.join(statements), params))

        # (session)-[r]-(agent)
        template = "MERGE (session :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                   "\nMERGE (agent :`{AGENT_LABEL}` :`{STORE_ID}` {{id: {{agent_id}} }})" \
                   "\nMERGE (session)-[r :`{REL}`]->(agent)"

        statements = [template.format(
            SESSION_LABEL=LABEL_SESSION,
            AGENT_LABEL=LABEL_AGENT,
            STORE_ID=agent.tenant,
            REL=REL_SESSION_TO_AGENT
        )]

        params = [neo4j.Parameter("agent_id", agent.id),
                  neo4j.Parameter("session_id", session.id)]

        queries.append(neo4j.Query(''.join(statements), params))

        # Items

        for item in items:

            assert isinstance(item, Item)

            template = "MERGE (item :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})"

            statements = [template.format(
                ITEM_LABEL=LABEL_ITEM,
                STORE_ID=item.tenant
            )]

            params = [neo4j.Parameter("id", item.id)]

            for k, v in item.fields.items():

                if is_acceptable_data_type(v):
                    params.append(neo4j.Parameter(k, v))
                    statements.append(
                        "\nSET item.{0} = {{ {0} }}".format(
                            k
                        )
                    )

            queries.append(neo4j.Query(''.join(statements), params))

        # Actions

        for action in actions:

            assert isinstance(action, Action)

            if action.name == REL_ACTION_TYPE_VIEW:

                template = "MERGE (session :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                           "\nMERGE (item :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                           "\nMERGE (session)-[r :`{REL}`]->(item)"

                statements = [template.format(
                    SESSION_LABEL=LABEL_SESSION,
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=action.tenant,
                    REL=REL_ACTION_TYPE_VIEW
                )]

                for k in ("datetime",):

                    statements.append(
                        "\nSET r.{0} = {{ {0} }}".format(
                            k
                        )
                    )

                params = [neo4j.Parameter("datetime", action.timestamp),
                          neo4j.Parameter("item_id", action.item),
                          neo4j.Parameter("session_id", action.session)]

                queries.append(neo4j.Query(''.join(statements), params))

            elif action.name == REL_ACTION_TYPE_ADD_TO_CART:

                # (item)-[r]-(session)

                template = "MERGE (session :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                           "\nMERGE (item :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                           "\nMERGE (session)-[r :`{REL}`]->(item)"

                statements = [template.format(
                    SESSION_LABEL=LABEL_SESSION,
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=action.tenant,
                    REL=REL_ACTION_TYPE_ADD_TO_CART
                )]

                for k in ("datetime", "qty"):

                    statements.append(
                        "\nSET r.{0} = {{ {0} }}".format(
                            k
                        )
                    )

                params = [neo4j.Parameter("datetime", action.timestamp),
                          neo4j.Parameter("item_id", action.item),
                          neo4j.Parameter("session_id", action.session),
                          neo4j.Parameter("qty", action.fields["qty"])]

                queries.append(neo4j.Query(''.join(statements), params))

            elif action.name == REL_ACTION_TYPE_BUY:

                # (item)-[r]-(session)

                template = "MERGE (session :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                           "\nMERGE (item :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                           "\nMERGE (session)-[r :`{REL}`]->(item)"

                statements = [template.format(
                    SESSION_LABEL=LABEL_SESSION,
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=action.tenant,
                    REL=REL_ACTION_TYPE_BUY
                )]

                for k in ("datetime", "qty", "sub_total"):

                    statements.append(
                        "\nSET r.{0} = {{ {0} }}".format(
                            k
                        )
                    )

                params = [neo4j.Parameter("item_id", action.item),
                          neo4j.Parameter("session_id", action.session),
                          neo4j.Parameter("datetime", action.timestamp),
                          neo4j.Parameter("qty", action.fields["qty"]),
                          neo4j.Parameter("sub_total", action.fields["sub_total"])]

                queries.append(neo4j.Query(''.join(statements), params))

            elif action.name == REL_ACTION_TYPE_STARTED_CHECKOUT:

                template = "MERGE (session :`{SESSION_LABEL}` :`{STORE_ID}` {{id: {{session_id}} }})" \
                           "\nMERGE (item :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{item_id}} }})" \
                           "\nMERGE (session)-[r :`{REL}`]->(item)"

                statements = [template.format(
                    SESSION_LABEL=LABEL_SESSION,
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=action.tenant,
                    REL=REL_ACTION_TYPE_STARTED_CHECKOUT
                )]

                for k in ("datetime",):

                    statements.append(
                        "\nSET r.{0} = {{ {0} }}".format(
                            k
                        )
                    )

                params = [neo4j.Parameter("item_id", action.item),
                          neo4j.Parameter("session_id", action.session),
                          neo4j.Parameter("datetime", action.timestamp)]

                queries.append(neo4j.Query(''.join(statements), params))

            elif action.name == REL_ACTION_TYPE_SEARCH:

                template = "MERGE (session :`{SESSION_LABEL}` :`{STORE_ID}` {{ id: {{session_id}} }})" \
                           "\nMERGE (search :`{SEARCH_LABEL}` :`{STORE_ID}` {{ keywords: {{keywords}} }})" \
                           "\nMERGE (session)-[r :`{REL}`]->(search)"

                statements = [template.format(
                    SEARCH_LABEL=LABEL_SEARCH,
                    SESSION_LABEL=LABEL_SESSION,
                    STORE_ID=action.tenant,
                    REL=REL_ACTION_TYPE_SEARCH
                )]

                for k in ("datetime",):

                    statements.append(
                        "\nSET r.{0} = {{ {0} }}".format(
                            k
                        )
                    )

                params = [neo4j.Parameter("session_id", action.session),
                          neo4j.Parameter("datetime", action.timestamp),
                          neo4j.Parameter("keywords", action.fields["keywords"])]

                queries.append(neo4j.Query(''.join(statements), params))

            elif action.name in (REL_ACTION_TYPE_CHECK_DELETE_ITEM, REL_ACTION_TYPE_DELETE_ITEM):

                template = "MATCH (item :`{ITEM_LABEL}` :`{STORE_ID}` {{id: {{id}} }})" \
                           "\nOPTIONAL MATCH (item)-[r]-(x)" \
                           "\nDELETE r, item"

                statements = [template.format(
                    ITEM_LABEL=LABEL_ITEM,
                    STORE_ID=action.tenant
                )]

                params = [neo4j.Parameter("id", action.item)]

                queries.append(neo4j.Query(''.join(statements), params))

        return queries

    @classmethod
    def batch_import(cls, queries):

        try:

            neo4j.run_batch_query(queries, commit=True, timeout=60)

        except py2neo.cypher.error.transaction.DeadlockDetected as exc:

            Logger.error(exc)

            nap_time = 10

            Logger.info("Sleeping for {0}s".format(nap_time))
            time.sleep(nap_time)

            raise errors.ProcessFailureError("Neo4j deadlock")

        except http.SocketError as exc:

            Logger.error(exc)

            raise errors.ProcessFailureError("Socket timeout")
    #
    # @classmethod
    # def neo4j_shell_import(cls, queries):
    #
    #     if os.name == 'posix':
    #         for path in PATHS:
    #             os.environ["PATH"] = ''.join([os.environ["PATH"], os.pathsep, path])
    #
    #     neo4j_shell_path = shutil.which(NEO4J_SHELL)
    #
    #     if not neo4j_shell_path:
    #         raise ChildProcessError("Couldn't find {0} executable path".format(NEO4J_SHELL))
    #
    #     # use random uuid for file name. avoid race conditions
    #     file_name = str(uuid.uuid4())
    #     tmp_folder = tempfile.gettempdir()
    #     file_path = os.path.join(tmp_folder, file_name)
    #
    #     Logger.info("Writing queries to file `{0}`".format(file_path))
    #
    #     with open(file_path, "w", encoding="UTF-8") as f:
    #
    #         for query in queries:
    #
    #             for k, v in query.parameters.items():
    #                 if type(v) is str:
    #                     value = repr(v).strip("'")
    #                     s = u"\nexport {0}={1}\n".format(k, value)
    #                 else:
    #                     s = u"\nexport {0}={1}\n".format(k, v)
    #                 f.write(s)
    #
    #             s = u"{0};\n".format(query.query)
    #             f.write(s)
    #
    #     p = subprocess.Popen([neo4j_shell_path, "-file", file_path], stdout=subprocess.PIPE, shell=False)
    #
    #     output, err = p.communicate()
    #
    #     io.delete_file(file_path)
    #
    #     if p.returncode == 1:
    #
    #         msg = "Error importing data via {0}:\n\t{1}".format(NEO4J_SHELL, output)
    #         Logger.error(msg)
    #
    #         raise ChildProcessError(msg)
    #
    #     elif p.returncode == 0:
    #
    #         Logger.info("Successfully executed [{0}] queries".format(len(queries)))