#!/bin/bash

cd ../../../
PROJECTNAME=$(basename `pwd`)
ENV=$PROJECTNAME-env

PYTHONENV=./$ENV/bin
SRCROOT=./app/src
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

        echo "Done"
    fi
fi

