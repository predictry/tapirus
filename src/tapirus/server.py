'''
Created on 9 Jul, 2014

@author: frost
'''

"""
Predictry recommendation engine (Tapirus) RESTful server implemented using the
Flask-RESTful extension.
"""

from flask import Flask
from flask_restful import Api

from tapirus.api.v1.blueprints.resources.items import ItemAPI, ItemListAPI
from tapirus.api.v1.blueprints.resources.users import UserAPI, UserListAPI
from tapirus.api.v1.blueprints.resources.actions import ActionAPI, ActionListAPI
from tapirus.api.v1.blueprints.services.recommendation import RecommendationAPI


app = Flask(__name__)

api = Api(app)

#resources
api.add_resource(ItemAPI, '/tapirus/api/v1/items/<int:id>', '/tapirus/api/v1/items/<int:id>/', endpoint='item')
api.add_resource(ItemListAPI, '/tapirus/api/v1/items', '/tapirus/api/v1/items/', endpoint='items')
api.add_resource(UserAPI, '/tapirus/api/v1/users/<int:id>', '/tapirus/api/v1/users/<int:id>/', endpoint='user')
api.add_resource(UserListAPI, '/tapirus/api/v1/users', '/tapirus/api/v1/users/', endpoint='users')
api.add_resource(ActionAPI, '/tapirus/api/v1/actions/<int:id>', '/tapirus/api/v1/actions/<int:id>/', endpoint='action')
api.add_resource(ActionListAPI, '/tapirus/api/v1/actions', '/tapirus/api/v1/actions/', endpoint='actions')

#recommendations
api.add_resource(RecommendationAPI, '/tapirus/api/v1/recommend', '/tapirus/api/v1/recommend/', endpoint='recommend')

#run application
if __name__ == '__main__':
    #start listening for connection
    app.run(port=5000, debug=True)


#todo: do system checks
#todo: load app config from a file (e.g. location of log file config)
#TODO: log performance, and queries (i.e. the requests. the queries can be regenerated from them. The reverse is not as easy)