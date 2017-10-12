# Snafu: Snake Functions - LXC Executor

import os
import time
import lxc
#import io
#import sys
import tempfile

#def wrapper(func, funcargs):
#	print(func(*funcargs))

def wrapper(funcwithargs):
	print(funcwithargs[1](*funcwithargs[2:]), file=funcwithargs[0])

def execute(func, funcargs, envvars, sourceinfos):
	for envvar in envvars:
		os.environ[envvar] = envvars[envvar]

	c = lxc.Container("snafu")
	c.create("download", 0, {"dist": "alpine", "release": "3.6", "arch": "amd64"})
	success = c.start()
	if not success:
		raise Exception("LXC permissions insufficient")

	#channel = io.StringIO()
	channel = tempfile.TemporaryFile(mode="w+", buffering=1)

	stime = time.time()
	try:
		c.attach_wait(wrapper, (channel, func, *funcargs))
		channel.seek(0)
		res = channel.read().strip()
		success = True
	except Exception as e:
		res = e
		success = False
	dtime = (time.time() - stime) * 1000

	return dtime, success, res
