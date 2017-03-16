# Snafu: Snake Functions - Python2 Stateful Executor

#import json
import subprocess
#import pickle
#import base64
import threading
import queue
import os
import time

firstcall = {}

def asynccommand(command, commandprocess, qerr, qout, inputline, wait=True):
	def queuethread(out, queue):
		try:
			for line in iter(out.readline, b""):
				line = line.decode("utf-8").strip()
				queue.put(line)
		except Exception as e:
			pass

	if not commandprocess:
		commandprocess = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
	commandprocess.stdin.write(bytes(inputline + "\n", "utf-8"))
	commandprocess.stdin.flush()

	if not qout and not qerr:
		qout = queue.Queue()
		qerr = queue.Queue()
		tout = threading.Thread(target=queuethread, args=(commandprocess.stdout, qout))
		tout.daemon = True
		tout.start()
		terr = threading.Thread(target=queuethread, args=(commandprocess.stderr, qerr))
		terr.daemon = True
		terr.start()

	if not wait:
		return commandprocess, qerr, qout, ""

	results = ""
	had_output = False
	counter = 0
	while True:
		both_empty = True
		try:
			line = qout.get(timeout=0.001)
		except queue.Empty:
			pass
		else:
			had_output = True
			both_empty = False
			results += line
		try:
			line = qerr.get(timeout=0.001)
		except queue.Empty:
			pass
		else:
			#had_output = True
			both_empty = False
			#results += "(err)" + line
		if had_output and both_empty:
			return commandprocess, qerr, qout, results
		#counter += 1
		#if counter > 100:
		#	return commandprocess, qerr, qout, results

def execute_internal(func, funcargs, envvars, sourceinfos):
	global firstcall

	import_stmt1 = "import os"
	import_stmt2 = "os.chdir('{}')".format(os.path.dirname(sourceinfos.source))
	module = os.path.basename(sourceinfos.source)[:-3]
	import_stmt3 = "import {}".format(module)

	funcargsfmt = []
	for funcarg in funcargs:
		if type(funcarg) in (dict, list, int, float):
			funcargsfmt.append(str(funcarg))
		else:
			funcargsfmt.append("\"{}\"".format(str(funcarg)))
	funcargsfmt = ",".join(funcargsfmt)
	exec_stmt = "{}.{}({})".format(module, func.__name__, funcargsfmt)

	callid = threading.get_ident()
	if not callid in firstcall:
		proc, qerr, qout, r1 = asynccommand("python2 -iu", None, None, None, import_stmt1, wait=False)
		proc, qerr, qout, r2 = asynccommand(None, proc, qerr, qout, import_stmt2, wait=False)
		proc, qerr, qout, r3 = asynccommand(None, proc, qerr, qout, import_stmt3, wait=False)
		firstcall[callid] = proc, qerr, qout
	else:
		proc, qerr, qout = firstcall[callid]
	proc, qerr, qout, r4 = asynccommand(None, proc, qerr, qout, exec_stmt)

	#for i, funcarg in enumerate(funcargs):
	#	if "__class__" in dir(funcarg) and funcarg.__class__.__name__ == "SnafuContext":
	#		funcargs[i] = "pickle:" + base64.b64encode(pickle.dumps(funcarg, protocol=2)).decode("utf-8")
	# + envvars
	#funcargs = json.dumps(funcargs)
	#envvars = json.dumps(envvars)

	return r4.replace("'", "\"")

def execute(func, funcargs, envvars, sourceinfos):
	stime = time.time()

	try:
		res = execute_internal(func, funcargs, envvars, sourceinfos)
		success = True
	except Exception as e:
		res = e
		success = False
	dtime = (time.time() - stime) * 1000

	return dtime, success, res
