#!/bin/bash

function runUnitTests(){

    SOURCE="${BASH_SOURCE[0]}"

    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
      DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
      SOURCE="$(readlink "$SOURCE")"
      [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

    cd ${DIR}/../

    ENV=app-env
    PYTHONENV=${ENV}/bin
    UNITESTDIR=tests/unit
    SRCROOT=src
    TESTSROOT=tests

    FILES=`find ${UNITESTDIR} -name '*.py'`

    export PYTHONPATH=${PYTHONPATH}:${SRCROOT}
    export PYTHONPATH=${PYTHONPATH}:${TESTSROOT}
    ${PYTHONENV}/activate

    for f in ${FILES}; do
        ${PYTHONENV}/python ${f}
    done

}

runUnitTests
