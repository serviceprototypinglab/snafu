# Snafu: Snake Functions - Python3 Executor

import json
import subprocess
import pickle
import base64

def strbool(x):
	return True if x == "True" else False

def execute(func, funcargs, envvars, sourceinfos):
	for i, funcarg in enumerate(funcargs):
		if "__class__" in dir(funcarg) and funcarg.__class__.__name__ == "SnafuContext":
			funcargs[i] = "pickle:" + base64.b64encode(pickle.dumps(funcarg)).decode("utf-8")

	funcargs = json.dumps(funcargs)
	envvars = json.dumps(envvars)

	p = subprocess.run("python3 executors/python3-exec.py {} {} '{}' '{}'".format(sourceinfos.source, func.__name__, funcargs, envvars), stdout=subprocess.PIPE, shell=True)

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
