# Snafu: Snake Functions - Python Parser

import os
import ast
import importlib
import types
import sys
import json

def activatefile(self, source, convention, SnafuFunctionSource):
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

