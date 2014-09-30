#!/bin/bash

echo "Installing Oracle Java 8..."
sudo apt-get install software-properties-common -y --force-yes
sudo add-apt-repository ppa:webupd8team/java -y
sudo apt-get update
sudo echo debconf shared/accepted-oracle-license-v1-1 select true |   sudo debconf-set-selections
sudo echo debconf shared/accepted-oracle-license-v1-1 seen true |   sudo debconf-set-selections
sudo apt-get install oracle-java8-installer -y --force-yes

echo "Installing Neo4j..."
sudo wget -O - http://debian.neo4j.org/neotechnology.gpg.key| apt-key add -
sudo echo 'deb http://debian.neo4j.org/repo stable/' > /etc/apt/sources.list.d/neo4j.list
sudo apt-get update
sudo apt-get install neo4j -y --force-yes

echo "Configuring Neo4j..."
sudo cp  /var/lib/neo4j/conf/neo4j.properties /var/lib/neo4j/conf/neo4j.properties.bkp
sudo cp  ../conf/neo4j.properties /var/lib/neo4j/conf/neo4j.properties
sudo cp /etc/init.d/neo4j-service /etc/init.d/neo4j-service.bkp
sudo cp ../conf/neo4j-service.sh /etc/init.d/neo4j-service
sudo chmod +x /etc/init.d/neo4j-service

sudo service neo4j-service restart

echo "Done."