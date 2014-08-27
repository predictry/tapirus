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

$PYTHONENV/gunicorn -b unix:/tmp/unix_predictry_socket_1.sock --workers=4 --log-level=CRITICAL --name $APPNAME predictry.server:app &
$PYTHONENV/gunicorn -b unix:/tmp/unix_predictry_socket_2.sock --workers=4 --log-level=CRITICAL --name $APPNAME predictry.server:app &
$PYTHONENV/gunicorn -b unix:/tmp/unix_predictry_socket_3.sock --workers=4 --log-level=CRITICAL --name $APPNAME predictry.server:app &
$PYTHONENV/gunicorn -b unix:/tmp/unix_predictry_socket_4.sock --workers=4 --log-level=CRITICAL --name $APPNAME predictry.server:app &
#$PYTHONENV/gunicorn -b 0.0.0.0:8080 --worker-class gevent --debug --log-file error_logs.log --access-logfile acclogs.log --log-level debug --workers=5 --name $APPNAME predictry.server:app
