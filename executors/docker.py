# Snafu: Snake Functions - Docker Executor

import requests
import os
import configparser

def executecontrol(flaskrequest, tenant):
	endpoint = None

	# FIXME: construct endpoint by launching a docker container per tenant
	# FIXME: with some persistent or session-based mapping tenant->port number
	# FIXME: + volume mapping: functions-tenants/<tenant>

	headers = {}
	headers["X-Amz-Date"] = flaskrequest.headers.get("X-Amz-Date")

	data = flaskrequest.data.decode("utf-8")
	#method=r.method -> requests.post

	reply = requests.post(endpoint + flaskrequest.path, data=data, headers=headers)

	if reply.status_code == 200:
		return reply.content.decode("utf-8")
	else:
		return
