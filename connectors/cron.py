# Snafu: Snake Functions - Cron Connector

import threading
import time
import os
import configparser

gcb = None

def initinternal():
	connectconfig = 60
	if os.path.isfile("snafu.ini"):
		config = configparser.ConfigParser()
		config.read("snafu.ini")
		if "snafu" in config and "connector.cron" in config["snafu"]:
			connectconfig = int(config["snafu"]["connector.cron"])

	while True:
		time.sleep(connectconfig)
		# FIXME: choose correct function
		response = gcb("helloworld.helloworld", event="{}")

def init(cb):
	global gcb
	gcb = cb

	t = threading.Thread(target=initinternal, daemon=True)
	t.start()
