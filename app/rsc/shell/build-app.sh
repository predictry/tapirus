#!/bin/bash

function buildApp(){

    SOURCE="${BASH_SOURCE[0]}"
    while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
      DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
      SOURCE="$(readlink "$SOURCE")"
      [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
    done
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

    sudo bash ${DIR}/build-conf.sh

    #add PPAs
    sudo apt-get install software-properties-common -y --force-yes
    sudo add-apt-repository ppa:nginx/stable -y

    sudo apt-get update

    echo "Installing prerequisites..."
    sudo apt-get install python-dev python-pip python-virtualenv -y --force-yes
    sudo apt-get install gunicorn libevent-dev -y --force-yes
    sudo apt-get install nginx -y

    #shellshock bug update
    sudo apt-get install bash -y

    echo "Starting nginx.."
    sudo service nginx start

    echo "Stopping nginx..."
    sudo service nginx stop

    #check if files exist before backing up or deleting
    echo "Configuring nginx..."

    NGINX_CONF=/etc/nginx/nginx.conf

     if [ -f "$NGINX_CONF" ]; then
        sudo cp  ${NGINX_CONF} ${NGINX_CONF}.bkp
     fi

    sudo cp  ${DIR}/../conf/nginx-conf.conf /etc/nginx/nginx.conf
    sudo cp  ${DIR}/../conf/nginx.default /etc/nginx/sites-available/default
    sudo rm  /etc/nginx/sites-enabled/*
    sudo ln  -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
    sudo cp  ${DIR}/../conf/.htpasswd /etc/nginx/

    echo "Setting up to run on startup..."
    sudo cp  /etc/rc.local   /etc/rc.local.bkp
    sudo cp  ${DIR}/../conf/rc.local /etc/
    sudo chmod 755 /etc/rc.local

    echo "Starting nginx..."
    sudo service nginx start

    sudo rm ${DIR}/../conf/nginx-conf.conf
    sudo rm ${DIR}/../conf/nginx.default
    sudo rm ${DIR}/../conf/rc.local

    sudo bash ${DIR}/build-env.sh

    echo "Done."

}

buildApp