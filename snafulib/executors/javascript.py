# Snafu: Snake Functions - JavaScript Executor

import subprocess
import time
import os.path

def execute(func, funcargs, envvars, sourceinfos):
	sourcemodule = sourceinfos.source[:-3]

	if "." in func:
		func = func.split(".")[1]

	# exports hack
	sourcemodulemod = sourcemodule + ".js.export"
	if not os.path.isfile(sourcemodulemod):
		code = open(sourcemodule + ".js").read()
		if not "exports" in code:
			f = open(sourcemodulemod, "w")
			f.write(code)
			f.write("\n")
			f.write("function mainwrapper(input){console.log(main(input));}\n")
			f.write("exports.main = mainwrapper;\n")
			sourcemodule = sourcemodulemod
	else:
		sourcemodule = sourcemodulemod

	# message hack
	if not "{" in funcargs[0]:
		funcargs[0] = "\"{\"body\": {\"message\": \"%s\"}}\"" % funcargs[0]

	if sourcemodulemod != sourcemodule:
		cmd = "nodejs -e 'require(\"./%s\").%s(%s, {\"status\": function(x){return {\"send\": function(x){console.log(\"RET:\" + x)}}}})'" % (sourcemodule, func, funcargs[0])
	else:
		cmd = "nodejs -e 'require(\"./%s\").%s(%s)'" % (sourcemodule, func, funcargs[0])

	stime = time.time()
	p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
	out = p.stdout.decode("utf-8")
	dtime = time.time() - stime

	success = False
	res = []
	for line in out.split("\n"):
		if sourcemodulemod != sourcemodule:
			if line.startswith("RET:"):
				success = True
				res = line[4:]
				break
		else:
			success = True
			res = line
			break

	return dtime, success, res
