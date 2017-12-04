# Snafu: Snake Functions - Main Module

import argparse
import os
import sys
#import pathlib
import ast
import importlib
import importlib.machinery
import types
import inspect
import time
import json
import hashlib
import base64
import glob
import subprocess
import shutil
import threading

executormapping = {
	"c": "so",
	"docker": None,
	"inmemory": "py",
	"lxc": "py",
	"inmemstateless": "py",
	"java": "class",
	"javascript": "js",
	"openshift": None,
	"proxy": None,
	"python2": "py",
	"python2stateful": "py",
	"python3": "py"
}

def selectexecutors(argsexecutor):
	executors = {"py": "inmemory", "js": "javascript", "class": "java", "so": "c"}
	for executor in argsexecutor:
		if executormapping[executor]:
			executors[executormapping[executor]] = executor
		else:
			for ex in executors:
				executors[ex] = executor
	executors = list(set(executors.values()))
	return executors

class SnafuFunctionSource:
	def __init__(self, source, scan=True):
		self.source = source
		self.size = None
		self.checksum = None
		self.content = None
		self.module = None
		if scan:
			self.size = os.stat(source).st_size
			self.content = open(source).read()
			self.checksum = base64.b64encode(hashlib.sha256(bytes(self.content, "utf-8")).digest()).decode("utf-8")

class SnafuImport:
	functiondir = None

	def prepare():
		if not SnafuImport.functiondir:
			SnafuImport.functiondir = "functions-local"
		os.makedirs(SnafuImport.functiondir, exist_ok=True)

	def importfunction(funcname, codezip, config, convert=False):
		#funcdir = os.path.join(SnafuImport.functiondir, funcname)
		funcdir = SnafuImport.functiondir
		if codezip:
			os.makedirs(funcdir, exist_ok=True)
			subprocess.run("cd {} && unzip -o -q ../{}".format(funcdir, os.path.basename(codezip)), shell=True)
		codefiles = glob.glob(os.path.join(funcdir, "*.py"))
		if len(codefiles) == 0:
			codefiles = glob.glob(os.path.join(funcdir, "*.java"))
		if len(codefiles) == 0:
			codefiles = glob.glob(os.path.join(funcdir, "*.class"))
		if len(codefiles) == 0:
			codefiles = glob.glob(os.path.join(funcdir, "*.js"))
		if len(codefiles) == 0:
			# FIXME: heuristics leading to non-usable Java function deployments
			codefiles = glob.glob(os.path.join(funcdir, "META-INF"))
		codefile = codefiles[0]
		oldcodefile = None
		if codezip:
			if convert and config["Runtime"] == "python2.7":
				oldcodefile = codefile.replace(".py", ".py2")
				shutil.copyfile(codefile, oldcodefile)
				subprocess.run("2to3 --no-diffs -nw {} 2>/dev/null".format(codefile), shell=True)
				config["Runtime"] = "python3"

		configfile = os.path.join(funcdir, os.path.basename(codefile).split(".")[0] + ".config")
		if config:
			#filename = config["Handler"].split(".")[0]
			#configfile = "functions-local/{}/{}.config".format(functionname, filename)
			f = open(configfile, "w")
			json.dump(config, f)

		return codefile, configfile, oldcodefile

class SnafuContext:
	def __init__(self):
		self.function_name = None
		self.function_version = None
		self.memory_limit_in_mb = 128

		self.timer = time.time()
		self.timelimit = 60

	def get_remaining_time_in_millis(self):
		return self.timelimit - (time.time() - self.timer)

class Snafu:
	def __init__(self, quiet=False):
		self.functions = {}
		self.quiet = quiet
		self.connectormods = []
		self.loggermods = []
		self.interactive = False
		#self.isolation = isolation
		self.executormods = []
		self.functionconnectors = {}
		self.threads = []
		self.externalexecutor = None
		self.configpath = None

	def setupexecutors(self, executors):
		if not self.quiet:
			for executor in executors:
				print("+ executor:", executor)

		self.executormods = []
		for executor in executors:
			mod = importlib.import_module("snafulib.executors." + executor)
			self.executormods.append(mod)

	def setuploggers(self, loggers):
		if "none" in loggers:
			return

		if not self.quiet:
			for logger in loggers:
				print("+ logger:", logger)

		self.loggermods = []
		for logger in loggers:
			mod = importlib.import_module("snafulib.loggers." + logger)
			self.loggermods.append(mod)

	def alert(self, s):
		col_on = "\x1b[31m\x1b[3m"
		col_off = "\x1b[0m"

		print(col_on + "{}".format(s) + col_off, file=sys.stderr)

	def info(self, s):
		if self.quiet and not self.interactive:
			return

		col_on = "\x1b[32m\x1b[1m"
		col_off = "\x1b[0m"

		timestamp = time.time()
		callid = threading.get_ident()

		print(col_on + "[{:.3f}][{}][{}]".format(timestamp, callid, s) + col_off)

	def executeexternal(self, funcname):
		if self.interactive:
			if os.isatty(sys.stdin.fileno()):
				data = input("Data for argument(s) may be needed...")
			else:
				data = sys.stdin.read().strip()

		tmpfile = "/tmp/_lambdaoutput.snafu"
		if self.externalexecutor == "lambda":
			cmd = "aws lambda invoke --function-name {} --payload '{}' {} >/dev/null".format(funcname, data, tmpfile)
		elif self.externalexecutor == "openwhisk":
			datafile = "/tmp/_wsk.snafu"
			f = open(datafile, "w")
			print(data, file=f)
			f.close()
			cmd = "wsk action invoke --blocking --result --param-file {} {} >{}".format(datafile, funcname, tmpfile)
		else:
			return None
		self.info("// execute {} on {}: {}".format(funcname, self.externalexecutor, cmd))

		stime = time.time()
		#dtime, success, res = executormod.execute(func, funcargs, envvars, sourceinfos)
		ret = os.system(cmd)
		success = not ret
		otime = (time.time() - stime) * 1000
		res = None
		if success:
			f = open(tmpfile)
			res = f.read()
			if "errorMessage" in res:
				success = False

		funcargs = []
		dtime = -1.0
		sourcename = "external:{}".format(self.externalexecutor)

		return self.reportexecutionresult(funcname, funcargs, success, res, dtime, otime, sourcename, configpath)

	def execute(self, funcname, **kwargs):
		asynccall = False
		funcnameargs = funcname.split(" ")
		if len(funcnameargs) > 1:
			for funcnamearg in funcnameargs:
				if funcnamearg == "async":
					asynccall = True
				else:
					funcname = funcnamearg

		if self.externalexecutor:
			return self.executeexternal(funcname)

		sourcename = None
		if "." in funcname:
			sourcename, funcnamepart = funcname.split(".")
		if funcname in self.functions:
			funcs = self.functions[funcname]
		else:
			self.alert("Error: {} is not a function.".format(funcname))
			return
		#if not sourcename:
		#	if len(funcs) == 1:
		#		func = list(funcs.values())[0]
		#	else:
		#		self.alert("Error: {} is ambiguous; qualifiers: {}.".format(funcname, list(funcs.keys())))
		#		return
		#else:
		#	if sourcename in funcs:
		#		func = funcs[sourcename]
		#	else:
		#		self.alert("Error: {}.{} is not a function.".format(sourcename, funcname))
		#		return

		func, config, sourceinfos = funcs

		self.info("function:{}".format(funcname))

		executormod = self.executormods[0]
		for executormodcandidate in self.executormods:
			candidatename = executormodcandidate.__name__.split(".")[-1]
			if sourceinfos.source.endswith(".py"):
				if executormapping[candidatename] == "py":
					executormod = executormodcandidate
			elif sourceinfos.source.endswith(".class"):
				if executormapping[candidatename] == "class":
					executormod = executormodcandidate
			elif sourceinfos.source.endswith(".so"):
				if executormapping[candidatename] == "so":
					executormod = executormodcandidate
			elif sourceinfos.source.endswith(".js"):
				if executormapping[candidatename] == "js":
					executormod = executormodcandidate

		envvars = {}
		if config:
			if "Environment" in config:
				envvars = config["Environment"]["Variables"]
				keys = ",".join(envvars.keys())
				self.info("config:environment:{}".format(keys))

		if ".java" in executormod.__name__ or ".javascript" in executormod.__name__ or ".c" in executormod.__name__:
			#wantedargs = []
			func, *wantedargs = func
		else:
			args = inspect.getargspec(func)
			wantedargs = args[0]
		funcargs = []
		for wantedarg in wantedargs:
			if wantedarg in kwargs:
				funcargs.append(kwargs[wantedarg])
			elif wantedarg == "context":
				# only for convention==lambda?
				ctx = SnafuContext()
				ctx.function_name = funcname
				funcargs.append(ctx)
			else:
				if self.interactive:
					if os.isatty(sys.stdin.fileno()):
						data = input("Data for argument {} needed:".format(wantedarg))
					else:
						data = sys.stdin.read().strip()
					# FIXME: heuristics - based on name or on presence of curly braces?
					if wantedarg == "event" or data.startswith("{"):
						try:
							data = json.loads(data)
						except:
							self.alert("Warning: JSON parsing has failed.")
					funcargs.append(data)
				else:
					self.alert("Error: Data for argument {} needed but not supplied.".format(wantedarg))
					return

		configpath = self.configpath

		if asynccall:
			self.info("async...")
			self.executeasync(func, funcargs, envvars, sourceinfos, sourcename, funcname, executormod, configpath)
			return

		return self.executeasyncthread(func, funcargs, envvars, sourceinfos, sourcename, funcname, executormod, configpath)

	def executeasync(self, func, funcargs, envvars, sourceinfos, sourcename, funcname, executormod, configpath):
		t = threading.Thread(target=self.executeasyncthread, args=(func, funcargs, envvars, sourceinfos, sourcename, funcname, executormod, configpath))
		t.setDaemon(True)
		t.start()

		self.threads.append(t)

	def executeasyncthread(self, func, funcargs, envvars, sourceinfos, sourcename, funcname, executormod, configpath):
		stime = time.time()
		dtime, success, res = executormod.execute(func, funcargs, envvars, sourceinfos)
		otime = (time.time() - stime) * 1000

		return self.reportexecutionresult(funcname, funcargs, success, res, dtime, otime, sourcename, configpath)

	def reportexecutionresult(self, funcname, funcargs, success, res, dtime, otime, sourcename, configpath):
		self.info("response:{}/{}".format(funcname, funcargs))
		if success:
			self.info("result:{}".format(res))
		else:
			self.alert("exception! [{}]".format(res))
		if dtime > 0:
			self.info("time:{:1.3f}ms".format(dtime))
		self.info("overalltime:{:1.3f}ms".format(otime))

		for loggermod in self.loggermods:
			loggermod.log(sourcename or "", funcname, dtime, success, configpath)

		return res

	def connect(self, connectors, configpath):
		if not self.quiet:
			for connector in connectors:
				print("+ connector:", connector)
				if connector == "cli":
					self.interactive = True

		connectormods = []
		for connector in connectors:
			mod = importlib.import_module("snafulib.connectors." + connector)
			connectormods.append(mod)

		for connectormod in connectormods:
			if "init" in dir(connectormod):
				connectormod.init(self.execute, None, configpath)

		for function in self.functionconnectors:
			if not self.quiet:
				print("+ connector for function", function)
			for connectormod in connectormods:
				if "init" in dir(connectormod):
					connectormod.init(self.execute, function, self.functionconnectors[function])

		self.connectormods = connectormods

		while True:
			for connectormod in connectormods:
				handled = False
				if "request" in dir(connectormod):
					handled = True
					f = connectormod.request()
					if not f:
						continue
					res = self.execute(f)
					connectormod.reply(res)
			if not handled:
				time.sleep(5)

	def activatejavascriptfile(self, source, convention):
		if not self.quiet:
			print("» javascript module:", source)

		try:
			import pyesprima.pyesprima3
		except:
			if not self.quiet:
				print("Warning: javascript parser not ready for {}, skipping.".format(source), file=sys.stderr)
			return

		#pyesprima.pyesprima3.unichr = chr

		try:
			ast = pyesprima.pyesprima3.parse(open(source).read())
		except Exception as e:
			if not self.quiet:
				print("Warning: {} is not parseable, skipping. [{}]".format(source, e), file=sys.stderr)
			return

		for body in ast.body:
			if body.type == "FunctionDeclaration":
				funcname = body["id"]["name"]
				if funcname == "main":
					funcname = os.path.basename(source).split(".")[0] + "." + funcname
					if not self.quiet:
						print("  function: {}".format(funcname))
					sourceinfos = SnafuFunctionSource(source, scan=False)
					funcparams = ["input"]
					self.functions[funcname] = ([funcname] + funcparams, None, sourceinfos)
				else:
					if not self.quiet:
						print("  skip function {}".format(funcname))
			elif body.type == "ExpressionStatement":
				if body.expression.left.type == "MemberExpression":
					if body.expression.left.object.name == "exports":
						funcname = body.expression.left.property.name
						funcname = os.path.basename(source).split(".")[0] + "." + funcname
						if not self.quiet:
							print("  function: {}".format(funcname))
						sourceinfos = SnafuFunctionSource(source, scan=False)
						funcparams = ["req", "res"]
						self.functions[funcname] = ([funcname] + funcparams, None, sourceinfos)

	def activatejavafile(self, source, convention):
		if not os.path.isfile("snafulib/executors/java/JavaExec.class"):
			pwd = os.getcwd()
			os.chdir("snafulib/executors/java")
			os.system("javac JavaExec.java")
			os.chdir(pwd)

		funcname = None
		configname = source.split(".")[0] + ".config"
		if os.path.isfile(configname):
			if not self.quiet:
				print("  config:", configname)
			config = json.load(open(configname))
			if config:
				funcname = config["FunctionName"]
		else:
			if convention == "lambda":
				if not self.quiet:
					print("  skip source {}".format(source))
				return

		if source.endswith(".java"):
			binfile = source.replace(".java", ".class")
			if not os.path.isfile(binfile):
				if not self.quiet:
					print("» java source:", source)
				pwd = os.getcwd()
				os.chdir(os.path.dirname(source))
				os.system("javac {}".format(os.path.basename(source)))
				os.chdir(pwd)
				source = binfile
			else:
				return

		if not self.quiet:
			print("» java module:", source)

		if funcname:
			# FIXME: shortcut leading to non-executable code for Lambda-imported Java
			if not self.quiet:
				print("  function: {}".format(funcname))
			sourceinfos = SnafuFunctionSource(source, scan=False)
			self.functions[funcname] = ([funcname], None, sourceinfos)
			return

		#javacmd = "java -cp executors/java/:{} JavaExec {} fib 3".format(os.path.dirname(source), os.path.basename(source).split(".")[0])
		#javacmd = "java JavaExec Hello myHandler 5 null"
		#print("JAVA", javacmd)
		javacmd = "java -cp snafulib/executors/java/:{} JavaExec {} SCAN".format(os.path.dirname(source), os.path.basename(source).split(".")[0])
		#os.system(javacmd)
		out, err = subprocess.Popen(javacmd, shell=True, stdout=subprocess.PIPE).communicate()
		for funcname in out.decode("utf-8").split("\n"):
			if not funcname:
				continue
			funcname, *funcparams = funcname.split(" ")
			funcname = os.path.basename(source).split(".")[0] + "." + funcname
			if not self.quiet:
				print("  function: {}".format(funcname))
			sourceinfos = SnafuFunctionSource(source, scan=False)
			self.functions[funcname] = ([funcname] + funcparams, None, sourceinfos)

	def activatecfile(self, source, convention):
		if not os.path.isfile("snafulib/executors/java/cexec"):
			pwd = os.getcwd()
			os.chdir("snafulib/executors/c")
			os.system("gcc -Wall -O2 -o cexec cexec.c -ldl")
			os.chdir(pwd)

		if source.endswith(".c"):
			binfile = source.replace(".c", ".so")
			if not os.path.isfile(binfile):
				if not self.quiet:
					print("» c source:", source)
				pwd = os.getcwd()
				os.chdir(os.path.dirname(source))
				os.system("gcc -Wall -O2 -fPIC -shared -o {} {}".format(os.path.basename(binfile), os.path.basename(source)))
				os.chdir(pwd)
				source = binfile
			else:
				return

		if not self.quiet:
			print("» c module:", source)

		funcname = os.path.basename(source).replace(".", "_") + ".handler"
		funcparams = ["input"]
		if not self.quiet:
			print("  function: {} (unchecked)".format(funcname))
		sourceinfos = SnafuFunctionSource(source, scan=False)
		self.functions[funcname] = ([funcname] + funcparams, None, sourceinfos)

	def activatefile(self, source, convention):
		sourceinfos = None
		try:
			sourceinfos = SnafuFunctionSource(source)
			sourcecode = sourceinfos.content
		except:
			print("Warning: {} is not parseable, skipping.".format(source), file=sys.stderr)
			return
		if not self.quiet:
			print("» module:", source)

		handler = None
		config = None
		configname = source.split(".")[0] + ".config"
		if os.path.isfile(configname):
			if not self.quiet:
				print("  config:", configname)
			config = json.load(open(configname))
			if config:
				if "Handler" in config:
					handler = config["Handler"]

		connectorconfig = None
		connectorconfigname = source.split(".")[0] + ".ini"
		if os.path.isfile(connectorconfigname):
			if not self.quiet:
				print("  connectors:", connectorconfigname)
			connectorconfig = connectorconfigname

		sourcetree = ast.parse(sourcecode)
		loader = importlib.machinery.SourceFileLoader(os.path.basename(source), source)
		mod = types.ModuleType(loader.name)
		sourceinfos.module = mod
		if not os.path.dirname(source) in sys.path:
			sys.path.append(os.path.dirname(source))
		try:
			loader.exec_module(mod)
		except Exception as e:
			if not self.quiet:
				print("  Warning: skipping due to import error: {}".format(e))
			return
		sourcename = os.path.basename(source).split(".")[0]
		for node in ast.walk(sourcetree):
			if type(node) == ast.FunctionDef:
				if not handler:
					handlername = "lambda_handler"
					handlerbase = sourcename
				else:
					handlerbase, handlername = handler.split(".")
				if convention not in ("lambda", "openwhisk") or (node.name == handlername and sourcename == handlerbase):
					funcname = sourcename + "." + node.name
					if config and "FunctionName" in config and convention in ("lambda", "openwhisk"):
						funcname = config["FunctionName"]
					try:
						func = getattr(mod, node.name)
					except:
						print("  skip method {}.{}".format(sourcename, node.name))
					else:
						if not self.quiet:
							print("  function: {}".format(funcname))
						#if not node.name in self.functions:
						#	self.functions[node.name] = {}
						#self.functions[node.name][sourcename] = (func, config, sourceinfos)
						self.functions[funcname] = (func, config, sourceinfos)
						if connectorconfig:
							self.functionconnectors[funcname] = connectorconfig
				else:
					if not self.quiet:
						print("  skip function {}.{}".format(sourcename, node.name))

	def activate(self, sources, convention, ignore=False):
		for source in sources:
			if os.path.isfile(source):
				if source.endswith(".py"):
					self.activatefile(source, convention)
				elif source.endswith(".java") or source.endswith(".class"):
					self.activatejavafile(source, convention)
				elif source.endswith(".c") or source.endswith(".so"):
					self.activatecfile(source, convention)
				elif source.endswith(".js"):
					self.activatejavascriptfile(source, convention)
			elif os.path.isdir(source):
				#p = pathlib.Path(source)
				entries = [os.path.join(source, entry.name) for entry in os.scandir(source) if not entry.name.startswith(".")]
				self.activate(entries, convention)
			else:
				if not ignore:
					print("Warning: {} is not readable, skipping.".format(source), file=sys.stderr)

class SnafuRunner:
	def add_common_arguments(parser):
		parser.add_argument("file", nargs="*", help="source file(s) or directories to activate; uses './functions' by default")
		parser.add_argument("-q", "--quiet", help="operate in quiet mode", action="store_true")
		parser.add_argument("-l", "--logger", help="function loggers; 'csv' by default", choices=["csv", "sqlite", "none"], default=["csv"], nargs="+")
		parser.add_argument("-e", "--executor", help="function executors; 'inmemory' by default", choices=["inmemory", "inmemstateless", "python2", "python2stateful", "java", "python3", "javascript", "c", "lxc"], default=["inmemory"], nargs="+")
		parser.add_argument("-s", "--settings", help="location of the settings file; 'snafu.ini' by default")

	def __init__(self):
		parser = argparse.ArgumentParser(description="Snake Functions as a Service")
		SnafuRunner.add_common_arguments(parser)
		parser.add_argument("-c", "--convention", help="method call convention", choices=["any", "lambda", "openwhisk"], default="any")
		parser.add_argument("-C", "--connector", help="function connectors; 'cli' by default", choices=["cli", "web", "messaging", "filesystem", "cron"], default=["cli"], nargs="+")
		parser.add_argument("-x", "--execute", help="execute a single function")
		parser.add_argument("-X", "--execution-target", help="execute function on target service", choices=["lambda", "gfunctions", "openwhisk"], nargs="?")
		args = parser.parse_args()

		ignore = False
		if not args.file:
			args.file.append("functions")
			args.file.append("functions-local")
			ignore = True

		snafu = Snafu(args.quiet)

		if args.execution_target and args.executor != ["inmemory"]:
			print("Error: -e/-X are mutually exclusive.", file=sys.stderr)
			exit(-1)

		if not args.execution_target:
			snafu.activate(args.file, args.convention, ignore=ignore)
		snafu.setuploggers(args.logger)

		if args.execution_target:
			snafu.externalexecutor = args.execution_target
			if not snafu.quiet:
				print("+ external executor: {}".format(snafu.externalexecutor))
		else:
			snafu.setupexecutors(selectexecutors(args.executor))

		snafu.configpath = args.settings

		if args.execute:
			snafu.interactive = True
			snafu.execute(args.execute)
		else:
			try:
				snafu.connect(args.connector, args.settings)
			except Exception as e:
				print()
				if str(e) != "":
					print("Terminated unexpectedly.")
					snafu.alert("[{}]".format(e))
				else:
					print("Terminated.")
			except KeyboardInterrupt:
				print()
				print("Terminated.")
