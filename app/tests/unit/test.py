__author__ = 'guilherme'


import json
from predictry.engine.graph.query.generator.resources.action import ActionQueryGenerator
from predictry.engine.graph.query.executor.executor import QueryExecutor


payload = json.load(open("../stream/actions/actions.json", "rb"))
args = {"domain": "safari"}

qgen = ActionQueryGenerator()
qexec = QueryExecutor()

for i in range(0, len(payload)):
    print "\n\nCreate Payload [{0}]".format(i)
    print "\n\nCreate Payload [{0}]".format(i)
    q, p = qgen.create(args, payload[i])

    print q
    print p

    #r, err = qexec.run(query=q, params=p, commit=True)

    #print "Result:", r
    #print "Error:", err

    print "\n\nRead Payload [{0}]".format(i)
    q, p = qgen.read({"id": 1, "domain": "redmart", "fields": "timestamp,name"})

    print q
    print p

    q, p = qgen.read({"domain": "redmart", "fields": "timestamp,name", "limit": 10, "offset": 5})

    print q
    print p

    #r, err = qexec.run(query=q, params=p, commit=True)

    #print "Result:", r
    #print "Error:", err

    print "\n\nUpdate Payload [{0}]".format(i)
    q, p = qgen.update({"id": 1, "domain": "redmart"}, payload[i])

    print q
    print p

    #r, err = qexec.run(query=q, params=p, commit=True)

    #print "Result:", r
    #print "Error:", err

    print "\n\nDelete Payload [{0}]".format(i)
    q, p = qgen.delete({"id": 1, "domain": "redmart"})

    print q
    print p

    #r, err = qexec.run(query=q, params=p, commit=True)

    #print "Result:", r
    #print "Error:", err