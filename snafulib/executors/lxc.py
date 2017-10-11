# Snafu: Snake Functions - LXC Executor

import os
import time
import lxc

def execute(func, funcargs, envvars, sourceinfos):
	for envvar in envvars:
		os.environ[envvar] = envvars[envvar]

	c = lxc.Container("snafu")
	c.create("download", 0, {"dist": "alpine", "release": "3.6", "arch": "amd64"})
	success = c.start()
	if not success:
		raise Exception("LXC permissions insufficient")

	stime = time.time()
	try:
		#res = func(*funcargs)
		c.attach(func, funcargs[0])
		res = 999999
		success = True
	except Exception as e:
		res = e
		success = False
	dtime = (time.time() - stime) * 1000

	return dtime, success, res
