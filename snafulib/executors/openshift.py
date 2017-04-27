# Snafu: Snake Functions - OpenShift Executor

import requests
import os
import configparser
import subprocess

container = "jszhaw/snafu"

endpoints = {}

def executecontrol(flaskrequest, tenant):
	if not tenant in endpoints:
		username = os.getenv("OPENSHIFT_USERNAME")
		password = os.getenv("OPENSHIFT_PASSWORD")
		password = os.getenv("OPENSHIFT_PROJECT")
		if not username or not password or not project:
			return
		os.system("oc login https://console.appuio.ch/ --username={} --password={}".format(username, password))
		os.system("oc project {}".format(project))
		os.system("oc new-app --name snafu-{} jszhaw/snafu".format(tenant))
		p = subprocess.run("oc status | grep svc/snafu-{} | cut -d " " -f 3".format(tenant), shell=True, stdout=subprocess.PIPE)

		endpoints[tenant] = "http://{}".format(p.decode("utf-8"))
		# FIXME: mounting the tenant's volume container to /opt/functions-local
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
