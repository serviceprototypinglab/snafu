# Snafu: Snake Functions - Java Parser

import os
import subprocess

def activatefile(self, source, convention, SnafuFunctionSource):
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

