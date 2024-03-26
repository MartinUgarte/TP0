#!/bin/bash
docker build -t ej3_image .
docker run --rm --network tp0_testing_net ej3_image > result.txt
result=$(cat result.txt)
[ "$result" == "test" ] && echo "Mensaje recibido correctamente" || echo "Mensaje no recibido correctamnte"
rm result.txt