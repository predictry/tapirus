#!/bin/bash

n=50
c=1
#host="http://localhost/"
host="http://localhost:5000/predictry/api/v1/recommend/?itemId=5550&type=oiv"

ab -n $n -c $c $host