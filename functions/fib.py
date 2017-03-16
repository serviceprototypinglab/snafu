import time
import math
import json
from boto3 import client as boto3_client
lambda_client = boto3_client('lambda', endpoint_url='http://localhost:10000')

lambda_client._endpoint.timeout = 300

def fib(x):
	msg = {"x": x}
	import sys
	fullresponse = lambda_client.invoke(FunctionName="fib.lambda_handler", Payload=json.dumps(msg))
	response = json.loads(fullresponse["Payload"].read().decode("utf-8"))
	return response["ret"]

def lambda_handler(event, context):
	x = event["x"]
	if x in (1, 2):
		return {"ret": 1}
	ret = fib(x - 1) + fib(x - 2)
	ret = {'ret': ret}
	return ret
