# Snafu: Snake Functions - Java Executor

#import json
import subprocess
#import pickle
#import base64
import os

def execute(func, funcargs, envvars, sourceinfos):
	#for i, funcarg in enumerate(funcargs):
	#	if "__class__" in dir(funcarg) and funcarg.__class__.__name__ == "SnafuContext":
	#		funcargs[i] = "pickle:" + base64.b64encode(pickle.dumps(funcarg, protocol=2)).decode("utf-8")
	#
	#funcargs = json.dumps(funcargs)
	#envvars = json.dumps(envvars)
	#
	#p = subprocess.run("python2 executors/python2-exec.py {} {} '{}' '{}'".format(sourceinfos.source, func.__name__, funcargs, envvars), stdout=subprocess.PIPE, shell=True)
	#
	#dtime, success, *res = p.stdout.decode("utf-8").strip().split(" ")
	#dtime = float(dtime)
	#success = strbool(success)
	#res = " ".join(res)
	##print("PY2", res)
	#return dtime, success, res

	classname = os.path.basename(sourceinfos.source).split(".")[0]
	methodname = "fib"
	#funcargs = {"n": 3}
	funcargs = ["3"]

	#print(">> call", classname, methodname, funcargs, envvars, sourceinfos.source)

	#classname, methodname = func.split(".")
	javacmd = "java -cp executors/java/:{} JavaExec {} {} {}".format(os.path.dirname(sourceinfos.source), classname, methodname, " ".join(funcargs))
	#print(">> javacmd", javacmd)
	out, err = subprocess.Popen(javacmd, shell=True, stdout=subprocess.PIPE).communicate()
	#print(">> result", out)

	out = out.decode("utf-8").split("\n")[-2]

	return 0.0, True, out
