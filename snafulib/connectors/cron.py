# Snafu: Snake Functions - Cron Connector

import threading
import time
import os
import configparser

gcb = None

def initinternal(function, configpath):
	connectconfig = None
	if not configpath:
		configpath = "snafu.ini"
	if not function:
		function = "snafu"
	if os.path.isfile(configpath):
		config = configparser.ConfigParser()
		config.read(configpath)
		if function in config and "connector.cron" in config[function]:
			connectconfig = int(config[function]["connector.cron"])

	if connectconfig:
		while True:
			time.sleep(connectconfig)
			response = gcb(function, event="{}")

def init(cb, function=None, configpath=None):
	global gcb
	gcb = cb

	t = threading.Thread(target=initinternal, daemon=True, args=(function, configpath))
	t.start()
