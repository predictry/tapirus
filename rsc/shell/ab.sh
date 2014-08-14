#!/bin/bash

n=1000
c=10
#host="http://localhost/"
host="http://localhost:5000/predictry/api/v1/recommend/?itemId=10525&type=oipt&appid=pongo&domain=redmart"

ab -n $n -c $c $host