#!/bin/bash

function buildEnvironment(){

    SOURCE="${BASH_SOURCE[0]}"

    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
      DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
      SOURCE="$(readlink "$SOURCE")"
      [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

    cd ${DIR}/../../../
    PROJECTNAME=$(basename `pwd`)
    ENV=$PROJECTNAME-env
    REQUIREMENTS=./app/rsc/requirements.txt

    virtualenv $ENV

    PYTHONENV=./${ENV}/bin
    SRCROOT=./app/src

    #activate env and add project src to PYTHONPATH
    chmod +x $PYTHONENV/activate
    $PYTHONENV/activate

    export PYTHONPATH=$PYTHONPATH:$SRCROOT

    $PYTHONENV/pip install -r $REQUIREMENTS
}

buildEnvironment