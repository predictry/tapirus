__author__ = 'guilherme'

from predictry.engine.models.resources.item import ItemSchema
from predictry.engine.models.resources.session import SessionSchema
from predictry.engine.graph.query.executor.executor import QueryExecutor
from predictry.utils.log.logger import Logger


def get_domains():

    q = "MATCH (x:item) RETURN DISTINCT labels(x) as labels"

    qexec = QueryExecutor()
    output, err = qexec.run(q)

    if err:
        Logger.error(err)
        return None, err

    domains = []

    for r in output:
        v = [x for x in r["labels"] if x not in ["item"]]
        domains.extend(v)

    Logger.debug("Domains: [%s]", domains)

    return domains


def store_results(domain, rtype, data):

    items = []
    matches = []

    for match in data:
        items.append(match["id"])
        matches.append(match["matches"])

    q = "MATCH (n:%s:%s {rtype: {rtype}}) DELETE n" % (domain, "trend")
    params = dict(rtype=rtype)

    output, err = execute_query(q, params, commit=True)

    if err:
        return False

    q = "CREATE (n:%s:%s {rtype: {rtype}, items:{items}, matches:{matches}," \
        "updated: timestamp()})" \
        % (domain, "trend")
    params = dict(rtype=rtype, items=items, matches=matches)

    output, err = execute_query(q, params, commit=True)

    if err:
        return False

    return True


def generate_query(domain, rtype):

    query = []
    params = {}

    action = lambda x: {
        "trv": "view",
        "trp": "buy",
        "trac": "add_to_cart"
    }[x]

    query.append("MATCH (s :%s:%s)-[r :%s]->(x :%s:%s)\n"
                 % (domain, SessionSchema.get_label(), action(rtype),
                    domain, ItemSchema.get_label()))

    query.append("WITH s,r,x\n"
                 "ORDER BY r.timestamp DESC\n"
                 "LIMIT 1000\n"
                 "RETURN DISTINCT x.id AS id, COUNT(x.id) AS matches")

    query.append("\n")
    query.append("ORDER BY matches DESC\n"
                 "LIMIT {limit}")

    params["limit"] = 20

    return ''.join(query), params


def execute_query(q, params, commit=False):

    qexec = QueryExecutor()
    output, err = qexec.run(q, params, commit=commit)

    if err:
        Logger.error(err)
        return None, err

    return output, None


def run():

    domains = get_domains()

    for domain in domains:
        for rtype in ["trv", "trp", "trac"]:
            q, params = generate_query(domain, rtype)

            output, err = execute_query(q, params)

            if err:
                Logger.warning("Failed to update trending items: [%s] for [%s]" % (rtype, domain))
                return

            if store_results(domain, rtype, output):
                Logger.info("Updated trending items: [%s] for [%s]" % (rtype, domain))