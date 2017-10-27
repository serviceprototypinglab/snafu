# Snafu: Snake Functions - Python3 Executor (Exec Module)

import sys
import os
import time
import json
import base64
import pickle

class Context:
	def __init__(self):
		self.SnafuContext = self
#****************************************************************************
#* This is just the method I used for the initial tracing with sys.settrace	*
#****************************************************************************
def trace(frame, event, arg):
	if not 'tracetime' in globals():
		global tracetime
		tracetime = None
	if event=='call':
		out_file = open('testfile.txt','a')
		if tracetime==None:
			tracetime=time.time()
		else:
			helptime = time.time()
			timedif=int(round((helptime-tracetime)*1000000))
			out_file.write(' time taken: '+str(timedif)+' µs\n')
			tracetime = helptime
		line_no = frame.f_lineno
		funcname = frame.f_code.co_name
		filename = frame.f_code.co_filename
		caller = frame.f_back
		caller_funcname = caller.f_code.co_name
		caller_filename = caller.f_code.co_filename
		out_file.write(event+' to '+str(filename)+'.'+str(funcname)+' by '+caller_filename+'.'+caller_funcname)
	#print(event+' to '+str(filename)+'.'+str(funcname))

def execute(filename, func, funcargs, envvars):
	funcargs = json.loads(funcargs)
	envvars = json.loads(envvars)

	for i, funcarg in enumerate(funcargs):
		if type(funcarg) == str and funcarg.startswith("pickle:"):
			sys.modules["lib"] = Context()
			sys.modules["lib.snafu"] = Context()
			#funcarg = pickle.loads(base64.b64decode(funcarg.split(":")[1]))
			# FIXME: SnafuContext as in python2-exec module
			funcarg = None

	sys.path.append(".")
	os.chdir(os.path.dirname(filename))
	mod = __import__(os.path.basename(filename[:-3]))
	func = getattr(mod, func)

	for envvar in envvars:
		os.environ[envvar] = envvars[envvar]

	stime = time.time()
	try:
		#********************************************************************
		#*	This is where you activate your tracing,						*
		#*	because the next line executes code. 							*
		#*	The "sys.settrace(trace)" is how I did it in my first executor	*
		#********************************************************************
		sys.settrace(trace)
		res = func(*funcargs)

		#********************************************************************
		#*		This is where you deactivate your tracing again				*
		#********************************************************************
		sys.settrace(None)
		success = True
	except Exception as e:
		res = e
		success = False
	dtime = (time.time() - stime) * 1000

	#return dtime, success, res
	return "{} {} {}".format(dtime, success, "{}".format(res).replace("'", "\""))

print(execute(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
