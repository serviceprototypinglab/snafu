#!/bin/bash

ep=http://localhost:10000
if [ ! -z $1 ]
then
	ep=$1
fi

if [ ! -f functions/localfib.py ]
then
	echo "Error: Needs to run from root directory." >&2
	exit 1
fi

cp functions/localfib.py testfib.py
echo "def lambda_handler(c, e):return fib(10)" >> testfib.py
zip testfib.zip testfib.py
rm testfib.py

aws --endpoint-url $ep lambda create-function --function-name testfib --runtime python3.5 --role notimportant --handler testfib.lambda_handler --zip-file fileb:///$PWD/testfib.zip

aws --endpoint-url $ep lambda list-functions
