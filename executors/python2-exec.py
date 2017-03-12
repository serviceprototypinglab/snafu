# Snafu: Snake Functions - Python2 Executor (Exec Module)

import sys
import os
import time
import json

def execute(filename, func, funcargs, envvars):
	funcargs = json.loads(funcargs)
	envvars = json.loads(envvars)

	sys.path.append(".")
	os.chdir(os.path.dirname(filename))
	mod = __import__(os.path.basename(filename[:-3]))
	func = getattr(mod, func)

	for envvar in envvars:
		os.environ[envvar] = envvars[envvar]

	stime = time.time()
	try:
		res = func(*funcargs)
		success = True
	except Exception as e:
		res = e
		success = False
	dtime = (time.time() - stime) * 1000

	#return dtime, success, res
	return "{} {} {}".format(dtime, success, res)

print(execute(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
