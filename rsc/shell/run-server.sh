#!/bin/bash

cd ../../../
PROJECTNAME=$(basename `pwd`)
ENV=$PROJECTNAME-env

PYTHONENV=./$ENV/bin
SRCROOT=./app/src
APPNAME=predictry

#activate env and add project src to PYTHONPATH
chmod +x $PYTHONENV/activate
$PYTHONENV/activate

export PYTHONPATH=$PYTHONPATH:$SRCROOT

$PYTHONENV/gunicorn -b 0.0.0.0:8080 --debug --log-file error_logs.log --access-logfile acclogs.log --log-level debug --workers=5 --name $APPNAME v1.predictry.api.server.rest-server:app