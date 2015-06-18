#!/bin/sh


function run(){

    docker run -it -p 5000:80 -p 8082:8082 --name tapirus predictry/tapirus
}

run


