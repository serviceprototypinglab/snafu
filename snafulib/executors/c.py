# Snafu: Snake Functions - C Executor

import subprocess
import os
import time

def execute(func, funcargs, envvars, sourceinfos):
	#print(">> call", func, funcargs, envvars, sourceinfos.source)

	ccmd = "snafulib/executors/c/cexec {} {}".format(sourceinfos.source, " ".join(funcargs))
	stime = time.time()
	out, err = subprocess.Popen(ccmd, shell=True, stdout=subprocess.PIPE).communicate()
	dtime = (time.time() - stime) * 1000

	try:
		out = out.decode("utf-8").split("\n")[-2]
		success = True
	except:
		out = ""
		success = False

	return dtime, success, out
