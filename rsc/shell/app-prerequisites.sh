#!/bin/bash

echo "Installing prerequisites..."
sudo apt-get install python-dev python-pip python-virtualenv -y
sudo apt-get install gunicorn libevent-dev -y
sudo aptitude install nginx -y

echo "Starting nginx.."
sudo service nginx start

echo "Stopping nginx..."
sudo service nginx stop

echo "Configuring nginx..."
sudo cp  /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bkp
sudo cp  ../conf/nginx-conf.conf /etc/nginx/nginx.conf
sudo cp  ../conf/.htpasswd /etc/nginx/

echo "Starting nginx..."
sudo service nginx start

echo "Done."