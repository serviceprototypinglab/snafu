# Snafu: Snake Functions - Python2 Executor

#import os
#import time
import json
import subprocess

def execute(func, funcargs, envvars, sourceinfos):
	funcargs = json.dumps(funcargs)
	envvars = json.dumps(envvars)

	p = subprocess.run("python2 executors/python2-exec.py {} {} '{}' '{}'".format(sourceinfos.source, func.__name__, funcargs, envvars), stdout=subprocess.PIPE, shell=True)

	dtime, success, *res = p.stdout.decode("utf-8").strip().split(" ")
	dtime = float(dtime)
	success = bool(success)
	res = " ".join(res)
	#print("PY2", res)
	return dtime, success, res
