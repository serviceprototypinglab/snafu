# Snafu: Snake Functions

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

class SnafuContext:
	def __init__(self):
		self.function_name = None
		self.function_version = None
		self.memory_limit_in_mb = 128

	def get_remaining_time_in_millis(self):
		return 999999

class Snafu:
	def __init__(self, quiet=False):
		self.functions = {}
		self.quiet = quiet
		self.connectormods = []

	def info(self, s):
		col_on = "\x1b[32m\x1b[1m"
		col_off = "\x1b[0m"
		print(col_on + s + col_off)

	def execute(self, funcname, **kwargs):
		sourcename = None
		if "." in funcname:
			sourcename, funcname = funcname.split(".")
		if funcname in self.functions:
			funcs = self.functions[funcname]
		else:
			print("Error: {} is not a function.".format(funcname), file=sys.stderr)
			return
		if not sourcename:
			if len(funcs) == 1:
				func = list(funcs.values())[0]
			else:
				print("Error: {} is ambiguous; qualifiers: {}.".format(funcname, list(funcs.keys())), file=sys.stderr)
				return
		else:
			if sourcename in funcs:
				func = funcs[sourcename]
			else:
				print("Error: {}.{} is not a function.".format(sourcename, funcname), file=sys.stderr)
				return

		func, config = func
		self.info("function:{}".format(funcname))
		if config:
			if "Environment" in config:
				self.info("[config:environment]")
				envvars = config["Environment"]["Variables"]
				for envvar in envvars:
					os.environ[envvar] = envvars[envvar]

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
				if "cli" in self.connectormods:
					if os.isatty(sys.stdin.fileno()):
						data = input("Data for argument {} needed:".format(wantedarg))
					else:
						data = sys.stdin.read()
					funcargs.append(data)
				else:
					print("Data for argument {} needed but not supplied.".format(wantedarg))
					return

		stime = time.time()
		res = func(*funcargs)
		self.info("[result:{}]".format(res))
		dtime = (time.time() - stime) * 1000
		self.info("[time:{:1.3f}ms]".format(dtime))
		f = open("snafu.csv", "a")
		print("{},{},{:1.3f}".format(sourcename or "", funcname, dtime), file=f)
		return res

	def connect(self, connectors):
		if not self.quiet:
			for connector in connectors:
				print("+ connector:", connector)

		connectormods = []
		for connector in connectors:
			mod = importlib.import_module("connectors." + connector)
			connectormods.append(mod)

		for connectormod in connectormods:
			if "init" in dir(connectormod):
				connectormod.init(self.execute)

		self.connectormods = connectormods

		while True:
			for connectormod in connectormods:
				handled = False
				if "request" in dir(connectormod):
					f = connectormod.request()
					res = self.execute(f)
					connectormod.reply(res)
					handled = True
			if not handled:
				time.sleep(5)

	def activatefile(self, source, convention):
		try:
			sourcecode = open(source).read()
		except:
			print("Warning: {} is not parseable, skipping.".format(source), file=sys.stderr)
			return
		if not self.quiet:
			print("» module:", source)
		config = None
		configname = source.split(".")[0] + ".config"
		if os.path.isfile(configname):
			if not self.quiet:
				print("  config:", configname)
				config = json.load(open(configname))
		sourcetree = ast.parse(sourcecode)
		loader = importlib.machinery.SourceFileLoader(os.path.basename(source), source)
		mod = types.ModuleType(loader.name)
		loader.exec_module(mod)
		sourcename = os.path.basename(source).split(".")[0]
		for node in ast.walk(sourcetree):
			if type(node) == ast.FunctionDef:
				handlername = "lambda_handler"
				# FIXME: if configuration is present, this may be named differently
				if convention != "lambda" or node.name == handlername:
					if not self.quiet:
						print("  function: {}.{}".format(sourcename, node.name))
					func = getattr(mod, node.name)
					if not node.name in self.functions:
						self.functions[node.name] = {}
					self.functions[node.name][sourcename] = (func, config)

	def activate(self, sources, convention):
		for source in sources:
			if os.path.isfile(source):
				if source.endswith(".py"):
					self.activatefile(source, convention)
			elif os.path.isdir(source):
				#p = pathlib.Path(source)
				entries = [os.path.join(source, entry.name) for entry in os.scandir(source) if not entry.name.startswith(".")]
				self.activate(entries, convention)
			else:
				print("Warning: {} is not readable, skipping.".format(source), file=sys.stderr)

class SnafuRunner:
	def __init__(self):
		parser = argparse.ArgumentParser(description="Snake Functions as a Service")
		parser.add_argument("-c", "--convention", help="method call convention", choices=["any", "lambda"], default="any")
		parser.add_argument("-C", "--connector", help="function connectors", choices=["cli", "web", "messaging", "filesystem"], default=["cli"], nargs="+")
		parser.add_argument("-x", "--execute", help="execute a single function")
		parser.add_argument("-q", "--quiet", help="operate in quiet mode", action="store_true")
		parser.add_argument("file", nargs="*", help="source file(s) or directories to activate; uses './functions' by default")
		args = parser.parse_args()

		if not args.file:
			args.file.append("functions")
			args.file.append("functions-local")

		snafu = Snafu(args.quiet)
		snafu.activate(args.file, args.convention)
		if args.execute:
			snafu.execute(args.execute)
		else:
			try:
				snafu.connect(args.connector)
			except:
				print("Terminated.")
