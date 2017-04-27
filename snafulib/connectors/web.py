# Snafu: Snake Functions - Web Connector

import flask
import threading
import os
import configparser

app = flask.Flask("snafu")

gcb = None

@app.route("/invoke/<function>")
def invoke(function):
	response = gcb(function)
	if not response:
		flask.abort(500)
	return response

def initinternal(function, configpath):
	connectconfig = None
	if not configpath:
		configpath = "snafu.ini"
	if not function:
		function = "snafu"
	if os.path.isfile(configpath):
		config = configparser.ConfigParser()
		config.read(configpath)
		if function in config and "connector.web" in config[function]:
			connectconfig = int(config[function]["connector.web"])

	if connectconfig:
		app.run(host="0.0.0.0", port=connectconfig)

def init(cb, function=None, configpath=None):
	global gcb
	gcb = cb

	t = threading.Thread(target=initinternal, daemon=True, args=(function, configpath))
	t.start()
