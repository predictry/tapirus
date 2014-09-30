'''
Created on 9 Jul, 2014

@author: frost
'''
"""Predictry recommendation engine (Tapirus) RESTful server implemented using the
Flask-RESTful extension."""

from flask import Flask
from flask_restful import Api
#from werkzeug.contrib.fixers import ProxyFix

from predictry.api.v1.blueprints.resources.items import ItemAPI, ItemListAPI
from predictry.api.v1.blueprints.resources.users import UserAPI, UserListAPI
from predictry.api.v1.blueprints.resources.actions import ActionAPI, ActionListAPI
from predictry.api.v1.blueprints.services.recommendation import RecommendationAPI


#class ServerApp(Flask):
#    def __init__(self, *args, **rest):
#        # insert startup code here
#        Logger.setup_logging("../../rsc/conf/logging-config.json")
#        super(ServerApp, self).__init__(__package__, *args, **rest)
#    def initialize(self):
#        print "Checking thrusters..."
#

#todo:do system checks
#todo: load app config from a file (e.g. location of log file config)


app = Flask(__name__)
app.debug = False

api = Api(app)

#resources
api.add_resource(ItemAPI, '/predictry/api/v1/items/<int:id>', '/predictry/api/v1/items/<int:id>/', endpoint='item')
api.add_resource(ItemListAPI, '/predictry/api/v1/items', '/predictry/api/v1/items/', endpoint='items')
api.add_resource(UserAPI, '/predictry/api/v1/users/<int:id>', '/predictry/api/v1/users/<int:id>/', endpoint='user')
api.add_resource(UserListAPI, '/predictry/api/v1/users', '/predictry/api/v1/users/', endpoint='users')
api.add_resource(ActionAPI, '/predictry/api/v1/actions/<int:id>', '/predictry/api/v1/actions/<int:id>/', endpoint='action')
api.add_resource(ActionListAPI, '/predictry/api/v1/actions', '/predictry/api/v1/actions/', endpoint='actions')

#recommendations
api.add_resource(RecommendationAPI, '/predictry/api/v1/recommend', '/predictry/api/v1/recommend/', endpoint='recommend')

#run application
if __name__ == '__main__':
    #start listening for connection
    app.run(port=5000, debug=True)

#TODO: log performance, and queries (i.e. the requests. the queries can be regenerated from them. The reverse is not as easy)	