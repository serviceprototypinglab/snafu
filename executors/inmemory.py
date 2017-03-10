# Snafu: Snake Functions - In-Memory Executor

import os
import time

def execute(func, funcargs, envvars, sourceinfos):
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

	return dtime, success, res
