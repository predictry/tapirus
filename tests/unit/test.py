__author__ = 'guilherme'


import json
from predictry.engine.graph.query.generator.resources.action import ActionQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor


payload = json.load(open("../stream/actions/actions.json", "rb"))
args = {"domain": "safari"}

qgen = ActionQueryGenerator()
qexec = QueryExecutor()

for i in range(0, len(payload)):
    print "\n\nPayload [{0}]".format(i)
    q, p = qgen.create(args, payload[i])

    print q
    print p

    r, err = qexec.run(query=q, params=p, commit=True)

    print "Result:", r
    print "Error:", err