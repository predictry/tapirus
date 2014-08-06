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

$pythonenv/python -m line_profiler rest-server.py.lprof
