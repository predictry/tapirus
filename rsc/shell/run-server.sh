#!/bin/bash

pythonenv=./tapirus-env/bin
srcroot=./src
projecroot=$srcroot/predictry
#app=$projecroot/api/server/rest-server.py


appname=predictry

#activate env and add project src to PYTHONPATH
chmod +x $pythonenv/activate
$pythonenv/activate

export PYTHONPATH=$PYTHONPATH:$srcroot

#$pythonenv/gunicorn -b 0.0.0.0:8080 --debug --workers=5 --name $appname --pythonpath $srcroot predictry.api.server.wsgi:app
$pythonenv/gunicorn -b 0.0.0.0:5000 --debug --workers=5 --name $appname predictry.api.server.rest-server:app
