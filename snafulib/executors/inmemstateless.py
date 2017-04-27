# Snafu: Snake Functions - In-Memory Stateless (Isolated) Executor

import os
import time
import importlib.machinery

def execute(func, funcargs, envvars, sourceinfos):
	loader = importlib.machinery.SourceFileLoader(os.path.basename(sourceinfos.source), sourceinfos.source)
	loader.exec_module(sourceinfos.module)

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
