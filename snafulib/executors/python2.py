# Snafu: Snake Functions - Python2 Executor

import json
import subprocess
import pickle
import base64
import tempfile

def strbool(x):
	return True if x == "True" else False

def execute(func, funcargs, envvars, sourceinfos):
	for i, funcarg in enumerate(funcargs):
		if "__class__" in dir(funcarg) and funcarg.__class__.__name__ == "SnafuContext":
			funcargs[i] = "pickle:" + base64.b64encode(pickle.dumps(funcarg, protocol=2)).decode("utf-8")

	funcargs = json.dumps(funcargs)
	envvars = json.dumps(envvars)

	if len(funcargs) > 256:
		tf = tempfile.NamedTemporaryFile()
		tf.write(bytes(funcargs, "utf-8"))
		funcargs = "tempfile:" + tf.name

	p = subprocess.run("python2 snafulib/executors/python2-exec.py {} {} '{}' '{}'".format(sourceinfos.source, func.__name__, funcargs, envvars), stdout=subprocess.PIPE, shell=True)

	try:
		dtime, success, *res = p.stdout.decode("utf-8").strip().split(" ")
	except:
		dtime = 0.0
		success = False
		res = []
	dtime = float(dtime)
	success = strbool(success)
	res = " ".join(res)
	#print("PY2", res)
	return dtime, success, res
