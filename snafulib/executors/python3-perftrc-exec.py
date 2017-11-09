# Snafu: Snake Functions - Python3 Executor (Exec Module)

import sys
import os
import time
import json
import base64
import pickle
import psutil
import threading

class Context:
	def __init__(self):
		self.SnafuContext = self

	#def __new__(self):
	#	self.SnafuContext = self
	#	return self

frame_time_dict={'frame':time.time()}
metric_map = {}
def trace(frame, event, arg):
	proc=psutil.Process(os.getpid())
	#print(proc.cpu_percent(interval=0.2),file=sys.stderr)
	print(proc.connections(),file=sys.stderr)
	return trace

def execute(filename, func, funcargs, envvars):
	funcargs = json.loads(funcargs)
	envvars = json.loads(envvars)

	for i, funcarg in enumerate(funcargs):
		if type(funcarg) == str and funcarg.startswith("pickle:"):
			sys.modules["lib"] = Context()
			sys.modules["lib.snafu"] = Context()
			#funcarg = pickle.loads(base64.b64decode(funcarg.split(":")[1]))
			# FIXME: SnafuContext as in python2-exec module
			funcarg = None

	sys.path.append(".")
	os.chdir(os.path.dirname(filename))
	mod = __import__(os.path.basename(filename[:-3]))
	func = getattr(mod, func)

	for envvar in envvars:
		os.environ[envvar] = envvars[envvar]

	stime = time.time()
	try:
		#activate tracing
		sys.settrace(trace)
		res = func(*funcargs)
		#deactivate tracing
		sys.settrace(None)
		success = True
	except Exception as e:
		res = e
		success = False
	dtime = (time.time() - stime) * 1000

	#return dtime, success, res
	return "{} {} {}".format(dtime, success, "{}".format(res).replace("'", "\""))

print(execute(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
