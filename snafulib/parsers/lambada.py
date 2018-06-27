# Snafu: Snake Functions - Lambada (Python) Parser

import os
import importlib
import types
import sys
import lambadalib.lambada

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

	def moveinternal(moveglobals, function, arguments, body, local, lambdafunctions, imports, dependencies, tainted, features, role, debug, endpoint, globalvars, cfc):
		if not self.quiet:
			print("  function: {}".format(function))
		self.functions[function] = (moveglobals[function], None, sourceinfos)

	lambadalib.lambada.moveinternal = moveinternal
	lambadalib.lambada.move(mod.__dict__, local=True)
