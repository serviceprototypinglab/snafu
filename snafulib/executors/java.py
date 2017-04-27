# Snafu: Snake Functions - Java Executor

#import json
#import pickle
#import base64
import subprocess
import os
import time

def execute(func, funcargs, envvars, sourceinfos):
	classname = os.path.basename(sourceinfos.source).split(".")[0]
	methodname = func.split(".")[1]

	#print(">> call", classname, methodname, func, funcargs, envvars, sourceinfos.source)

	#classname, methodname = func.split(".")
	javacmd = "java -cp snafulib/executors/java/:{} JavaExec {} {} {}".format(os.path.dirname(sourceinfos.source), classname, methodname, " ".join(funcargs))
	#print(">> javacmd", javacmd)
	stime = time.time()
	out, err = subprocess.Popen(javacmd, shell=True, stdout=subprocess.PIPE).communicate()
	dtime = (time.time() - stime) * 1000
	#print(">> result", out)

	out = out.decode("utf-8").split("\n")[-2]

	return dtime, True, out
