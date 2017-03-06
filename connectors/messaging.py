# Snafu: Snake Functions - Messaging Connector

import kombu
import threading
import time
import os
import configparser

gcb = None

def initinternal():
	connecturl = "amqp://guest:guest@localhost:5672/"
	if os.path.isfile("snafu.ini"):
		config = configparser.ConfigParser()
		config.read("snafu.ini")
		if "snafu" in config and "connector.messaging" in config["snafu"]:
			connecturl = config["snafu"]["connector.messaging"]
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
			# FIXME: choose correct function and send back results
			response = gcb("helloworld.helloworld", event="{}")
	queue.close()

def init(cb):
	global gcb
	gcb = cb

	t = threading.Thread(target=initinternal, daemon=True)
	t.start()
