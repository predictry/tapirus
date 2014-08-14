#!/bin/bash

echo "REMOVING TAPIRUS/NEO4j SETUP"

echo "Stopping Nginx..."
sudo service nginx stop

echo "Stopping neo4j..."
sudo service neo4j-service stop

echo "Removing Neo4j..."
sudo apt-get remove neo4j -y
sudo rm -rf /etc/apt/sources.list.d/neo4j*

echo "Removing Oracle Java 8..."
sudo apt-get remove oracle-java8-installer -y
sudo rm -rf /etc/apt/sources.list.d/webupd8team-java*

echo "Removing nginx..."
sudo apt-get remove python-dev python-pip python-virtualenv -y
sudo apt-get remove gunicorn -y
sudo aptitude remove nginx -y

echo "Removing custom nginx configuration..."
sudo rm -rf /etc/nginx/nginx.conf

echo "Removing Neo4j custom configuration..."
sudo rm -rf  /var/lib/neo4j/conf/neo4j.properties /var/lib/neo4j/conf/neo4j.properties.bkp
sudo rm -rf /etc/init.d/neo4j-service /etc/init.d/neo4j-service.bkp

echo "Deleting /var/lib/neo4j"
sudo rm -rf /var/lib/neo4j*

echo "Done"