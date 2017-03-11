# Snafu: Snake Functions - Messaging Connector

import kombu
import threading
import time
import os
import configparser

gcb = None

def initinternal(function, configpath):
	connecturl = None
	if not configpath:
		configpath = "snafu.ini"
	if not function:
		function = "snafu"
	if os.path.isfile(configpath):
		config = configparser.ConfigParser()
		config.read(configpath)
		if function in config and "connector.messaging" in config[function]:
			connecturl = config[function]["connector.messaging"]

	if not connecturl:
		return

	print("(messaging:connecting)")
	connection = kombu.Connection(connecturl)
	connection.connect()
	print("(messaging:connected)")

	queue = connection.SimpleQueue("sslq")
	while True:
		try:
			message = queue.get(block=True, timeout=20)
		except:
			print("(messaging:pass)")
			pass
		else:
			print("(messaging:received {})".format(message.payload))
			message.ack()
			# FIXME: send back response as AMQP message
			response = gcb(function, event="{}")
	queue.close()

def init(cb, function=None, configpath=None):
	global gcb
	gcb = cb

	t = threading.Thread(target=initinternal, daemon=True, args=(function, configpath))
	t.start()
