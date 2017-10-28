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

	#def __new__(self):
	#	self.SnafuContext = self
	#	return self
frame_time_dict={'frame':time.time()}
def trace(frame, event, arg):
	#Potential optimization: put caller_string and function_string into a dictionary

	#getting what code was called
	line_no = frame.f_lineno
	funcname = frame.f_code.co_name
	filename = frame.f_code.co_filename
	function_string = str(filename)+'.'+str(funcname)

	#getting who called the code
	has_caller = frame.f_back is not None
	caller_string = ''
	if has_caller:
		caller = frame.f_back
		caller_funcname = caller.f_code.co_name
		caller_filename = caller.f_code.co_filename
		caller_string = caller_filename+'.'+caller_funcname

	if event=='call':
		#inserting start time for the frame
		frame_time_dict[frame]=time.time()
		print('call from \t'+caller_string+' to '+function_string,file=sys.stderr)
	if event=='return':
		#taking out the time for frame
		time_elapsed_ms = round((time.time()-frame_time_dict[frame])*1000,6)
		print('return from \t'+function_string+' to '+caller_string+' - time elapsed: '+str(time_elapsed_ms)+"ms",file=sys.stderr)

	#need to return tracefunc so that it still works after functioncalls
	return trace

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
		#activate tracing
		sys.settrace(trace)
		res = func(*funcargs)
		#deactivate tracing
		sys.settrace(None)
		success = True
	except Exception as e:
		res = e
		success = False
	dtime = (time.time() - stime) * 1000

	#return dtime, success, res
	return "{} {} {}".format(dtime, success, "{}".format(res).replace("'", "\""))

print(execute(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
