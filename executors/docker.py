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
		authmount = ""
		if True:
			accdb = os.path.expanduser("~/.snafu-accounts")
			accdir = os.path.expanduser("~/.snafu-accounts-tenants/{}".format(tenant))
			if os.getenv("HOME") == "/":
				accdb = "/root/.snafu-accounts"
				accdir = "/root/.snafu-accounts-tenants/{}".format(tenant)
			c = configparser.ConfigParser()
			try:
				c.read(accdb)
			except:
				pass
			else:
				sections = c.sections()
				secretkey = None
				for section in sections:
					ckeyid = c.get(section, "access_key_id")
					if ckeyid == tenant:
						secretkey = c.get(section, "secret_access_key")
						break

				if secretkey:
					authmount = "-v {}:/root/.aws".format(accdir)
					os.makedirs(accdir, exist_ok=True)

					c = configparser.ConfigParser()
					acc = "default"
					c.add_section(acc)
					c.set(acc, "aws_access_key_id", tenant)
					c.set(acc, "aws_secret_access_key", secretkey)
					f = open("{}/credentials".format(accdir), "w")
					c.write(f)

					c = configparser.ConfigParser()
					acc = "default"
					c.add_section(acc)
					c.set(acc, "region", "invalid")
					f = open("{}/config".format(accdir), "w")
					c.write(f)
		dockercmd = "docker run -d -p 127.0.0.1:{}:10000 -v /opt/functions-tenants/{}:/opt/functions-local {} {}".format(portnum, tenant, authmount, container)
		os.system(dockercmd)
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
