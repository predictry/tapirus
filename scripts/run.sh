#!/bin/sh


function run(){

    docker run -it -d -p 7870:80 -p 7872:8082 --name tapirus predictry/tapirus
}

run


