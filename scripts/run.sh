#!/bin/sh


function run(){

    docker run -it -p 5000:80 --name tapirus predictry/tapirus
}

run


