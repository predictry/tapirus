'''
Created on 9 Jul, 2014

@author: frost
'''
"""Predictry recommendation engine (Tapirus) RESTful server implemented using the
Flask-RESTful extension."""

#TODO: [LATER] migrate to python 3
#TODO: [URGENT] place entire code under v1 folder
#TODO: Review notes from: http://java.dzone.com/articles/10-caveats-neo4j-users-should

from flask import Flask
from flask.ext.restful import Api

from v1.predictry.api.server.apis.resources import ItemAPI, ItemListAPI, UserAPI, UserListAPI, ActionAPI, ActionListAPI
from v1.predictry.api.server.apis.services import RecommendationAPI

#app = Flask(__name__, static_url_path="")
app = Flask(__name__)
app.debug = True

api = Api(app)

#resources
api.add_resource(ItemAPI, '/predictry/api/v1/items/<int:id>/', endpoint='item')
api.add_resource(ItemListAPI, '/predictry/api/v1/items/', endpoint='items')
api.add_resource(UserAPI, '/predictry/api/v1/users/<int:id>/', endpoint='user')
api.add_resource(UserListAPI, '/predictry/api/v1/users/', endpoint='users')
api.add_resource(ActionAPI, '/predictry/api/v1/actions/<int:id>/', endpoint='action')
api.add_resource(ActionListAPI, '/predictry/api/v1/actions/', endpoint='actions')

#recommendations
api.add_resource(RecommendationAPI, '/predictry/api/v1/recommend/', endpoint='recommend')

if __name__ == '__main__':
    app.run(port=5000)


#TODO: log performance, and queries (i.e. the requests. the queries can be regenerated from them. The reverse is not as easy)