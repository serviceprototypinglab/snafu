# Snafu: Snake Functions - C Parser

import os

def activatefile(self, source, convention, SnafuFunctionSource):
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
