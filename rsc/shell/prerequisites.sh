#!/bin/bash

echo "Installing Oracle Java 8..."
sudo add-apt-repository ppa:webupd8team/java
sudo apt-get update
sudo apt-get install oracle-java8-installer -y

echo "Installing Neo4j..."
sudo wget -O - http://debian.neo4j.org/neotechnology.gpg.key| apt-key add -
sudo echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install neo4j -y

echo "Configuring Neo4j..."
sudo cp  /var/lib/neo4j/conf/neo4j.properties /var/lib/neo4j/conf/neo4j.properties.bkp
sudo cp  ../conf/neo4j.properties /var/lib/neo4j/conf/neo4j.properties
sudo cp /etc/init.d/neo4j-service /etc/init.d/neo4j-service.bkp
sudo cp ../conf/neo4j-service.sh /etc/init.d/neo4j-service
sudo chmod +x /etc/init.d/neo4j-service

sudo service neo4j-service restart

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