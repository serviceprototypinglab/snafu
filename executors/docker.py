# Snafu: Snake Functions - Docker Executor

import requests
import os
import configparser

container = "jszhaw/snafu"

endpoints = {}

def executecontrol(flaskrequest, tenant):
	if not tenant in endpoints:
		portnum = 10000 + len(endpoints) + 1
		endpoints[tenant] = "http://localhost:{}".format(portnum)
		os.system("docker run -d -p 127.0.0.1:{}:10000 -v /opt/functions-tenants/{}:/opt/functions-local {}".format(portnum, tenant, container))
	endpoint = endpoints[tenant]

	headers = {}
	headers["X-Amz-Date"] = flaskrequest.headers.get("X-Amz-Date")

	data = flaskrequest.data.decode("utf-8")
	#method=r.method -> requests.post

	reply = requests.post(endpoint + flaskrequest.path, data=data, headers=headers)

	if reply.status_code == 200:
		return reply.content.decode("utf-8")
	else:
		return
