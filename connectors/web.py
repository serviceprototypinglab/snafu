# Snafu: Snake Functions - Web Connector

import flask
import threading

app = flask.Flask("snafu")

gcb = None

@app.route("/invoke/<function>")
def invoke(function):
	response = gcb(function)
	if not response:
		flask.abort(500)
	return response

def initinternal():
	app.run(host="0.0.0.0", port=8080)

def init(cb):
	global gcb
	gcb = cb

	t = threading.Thread(target=initinternal, daemon=True)
	t.start()
