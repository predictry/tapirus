#!/bin/sh


function run(){

    docker run -it -d -p 7870:80 --name tapirus predictry/tapirus
}

run


