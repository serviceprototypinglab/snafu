# Snafu: Snake Functions - Proxy Executor

import requests
import os
import configparser

def executecontrol(flaskrequest, tenant):
	endpoint = None

	if tenant:
		c = configparser.ConfigParser()
		try:
			accdb = os.path.expanduser("~/.snafu-accounts")
			if os.getenv("HOME") == "/":
				accdb = "/root/.snafu-accounts"
			c.read(accdb)
		except:
			return
		sections = c.sections()
		for section in sections:
			ckeyid = c.get(section, "access_key_id")
			if ckeyid == tenant:
				endpoint = c.get(section, "endpoint")
				break
	else:
		config = configparser.ConfigParser()
		config.read("snafu.ini")
		if "snafu" in config and "executor.proxy" in config["snafu"]:
			endpoint= config["snafu"]["executor.proxy"]
	if not endpoint:
		return

	headers = {}
	headers["X-Amz-Date"] = flaskrequest.headers.get("X-Amz-Date")

	data = flaskrequest.data.decode("utf-8")
	#method=r.method -> requests.post

	reply = requests.post(endpoint + flaskrequest.path, data=data, headers=headers)

	if reply.status_code == 200:
		return reply.content.decode("utf-8")
	else:
		return
