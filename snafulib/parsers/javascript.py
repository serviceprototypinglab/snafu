# Snafu: Snake Functions - JavaScript Parser

def activatefile(self, source, convention, SnafuFunctionSource):
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
