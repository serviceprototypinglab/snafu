import time
import math
import json
import os
from boto3 import client as boto3_client

hostaccess = False

host = "localhost"
if hostaccess and os.path.isfile("/.dockerenv"):
	host = "172.17.0.1"

lambda_client = boto3_client('lambda', endpoint_url='http://{}:10000'.format(host))

lambda_client._endpoint.timeout = 300 # comment for reaper

def fib(x):
	msg = {"x": x}
	import sys
	fullresponse = lambda_client.invoke(FunctionName="fib.lambda_handler", Payload=json.dumps(msg))
	response = json.loads(fullresponse["Payload"].read().decode("utf-8"))
	return response["ret"]

def lambda_handler(event, context):
	#time.sleep(0.1) # uncomment for reaper
	x = event["x"]
	if x in (1, 2):
		return {"ret": 1}
	ret = fib(x - 1) + fib(x - 2)
	ret = {'ret': ret}
	return ret
