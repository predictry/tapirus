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

PIDDIR=pid
LOGDIR=log

if [ ! -d "$PIDDIR" ]; then
  mkdir $PIDDIR
fi

if [ ! -d "$LOGDIR" ]; then
  mkdir $LOGDIR
fi

n=$(echo `nproc`)

echo "Starting $n services..."

for (( i=1; i<=$n; i++ ))
do
    socket="/tmp/unix_predictry_socket_${i}.sock"
    pid="pid/server-${i}.pid"

    `$PYTHONENV/gunicorn -b unix:${socket} --workers=$n --log-level=CRITICAL --name $APPNAME predictry.server:app` & echo $! > ${pid}
done

echo "Starting background workers..."

$PYTHONENV/python -m predictry.workers & echo $! > "pid/workers.pid"

#chcek if program is still running
#PID=$(cat program.pid)
#if [ -e /proc/${PID} -a /proc/${PID}/exe -ef /usr/bin/program ]; then
#echo "Still running"
#fi

echo "Done."