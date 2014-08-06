#!/bin/bash

cd ../../../
PROJECTNAME=$(basename `pwd`)
ENV=$PROJECTNAME-env
REQUIREMENTS=./app/rsc/requirements.txt

virtualenv $ENV

pythonenv=./$ENV/bin
srcroot=./app/src

#activate env and add project src to PYTHONPATH
chmod +x $pythonenv/activate
$pythonenv/activate

export PYTHONPATH=$PYTHONPATH:$srcroot

$pythonenv/pip install -r $REQUIREMENTS


