# Snafu: Snake Functions - JavaScript Executor

import subprocess
import time

def execute(func, funcargs, envvars, sourceinfos):
	sourcemodule = sourceinfos.source[:-3]

	cmd = "nodejs -e 'require(\"./%s\").%s({\"body\": {\"message\": \"%s\"}}, {\"status\": function(x){return {\"send\": function(x){console.log(\"RET:\" + x)}}}})'" % (sourcemodule, func, funcargs[0])

	stime = time.time()
	p = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
	out = p.stdout.decode("utf-8")
	dtime = time.time() - stime

	success = False
	res = []
	for line in out.split("\n"):
		if line.startswith("RET:"):
			success = True
			res = line[4:]

	return dtime, success, res
