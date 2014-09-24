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

PYTHONENV=./$ENV/bin
SRCROOT=./app/src
APPNAME=predictry

#activate env and add project src to PYTHONPATH
chmod +x $PYTHONENV/activate
$PYTHONENV/activate

export PYTHONPATH=$PYTHONPATH:$SRCROOT

PIDDIR=pid
LOGDIR=log

function start(){

    n=$(echo `nproc`)

    echo "Starting $n instances..."

    for (( i=1; i<=$n; i++ ))
    do
        socket="/tmp/unix_predictry_socket_${i}.sock"
        pid="pid/server-${i}.pid"

        `$PYTHONENV/gunicorn -b unix:${socket} --workers=$n --log-level=CRITICAL --name $APPNAME predictry.server:app` & echo $! > ${pid}
    done

    echo "Starting background workers..."

    $PYTHONENV/python -m predictry.workers & echo $! > "pid/workers.pid"

    echo "Done."
}

if [ ! -d "$PIDDIR" ]; then
    mkdir $PIDDIR
fi

if [ ! -d "$LOGDIR" ]; then
    mkdir $LOGDIR
fi

if [ -d "$PIDDIR" ]; then

    if [ "$(ls -A $PIDDIR)" ]; then

        process=unix_predictry

        ps -ef | grep $process | grep -v -q grep

        if [ $?  -eq "0" ]; then
            echo "It seems that the server is already running."
            echo "Stop any running instances before running this command"
        else
            start
        fi
    else
        start
    fi
fi