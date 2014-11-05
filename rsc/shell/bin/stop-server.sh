#!/bin/bash

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

cd ${DIR}/../../../../
PROJECTNAME=$(basename `pwd`)
ENV=$PROJECTNAME-env

PYTHONENV=${DIR}/$ENV/bin
SRCROOT=${DIR}/app/src
APPNAME=predictry

PIDDIR=pid
LOGDIR=log

if [ -d "$PIDDIR" ]; then

    if [ "$(ls -A $PIDDIR)" ]; then
        FILES=$PIDDIR/*.pid
        for f in $FILES
        do
            pid=$(cat $f)
            CMD="kill -9 $pid"
            echo $CMD
            `$CMD`
            rm $f
        done

        CMD="pkill -f unix_predictry"
        echo $CMD
        `$CMD`

        echo "Service stopped."
    fi
fi

