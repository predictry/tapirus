#!/bin/bash

cd ../../../
PROJECTNAME=$(basename `pwd`)
ENV=$PROJECTNAME-env
REQUIREMENTS=./app/rsc/requirements.txt

virtualenv $ENV

PYTHONENV=./$ENV/bin
SRCROOT=./app/src

#activate env and add project src to PYTHONPATH
chmod +x $PYTHONENV/activate
$PYTHONENV/activate

export PYTHONPATH=$PYTHONPATH:$SRCROOT

$PYTHONENV/pip install -r $REQUIREMENTS


