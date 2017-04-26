# Snafu: Snake Functions - Import Utility Module

import argparse
import subprocess
import json
import os
import sys
import tempfile
import glob
import uuid

import snafulib.snafu

class SnafuImportUtility:
	def __init__(self):
		self.td = tempfile.TemporaryDirectory()

	def start_import(self):
		parser = argparse.ArgumentParser(description="Snake Functions as a Service - Import Utility")
		parser.add_argument("-s", "--source", help="import source", choices=["lambda", "gfunctions", "openwhisk"], default=None)
		parser.add_argument("-t", "--target", help="import target", choices=["snafu", "funktion", "fission", "kubeless"], default="snafu")
		parser.add_argument("-c", "--convert", help="convert functions from Python 2 to Python 3 for native execution")
		args = parser.parse_args()

		snafulib.snafu.SnafuImport.prepare()

		if args.source is None:
			print("Must specify a source with --source.", file=sys.stderr)
		elif args.source == "lambda":
			self.import_lambda(args.target, args.convert)
		elif args.source == "gfunctions":
			self.import_gfunctions(args.target)
		elif args.source == "openwhisk":
			self.import_openwhisk(args.target)

	def export_snafu(self, filename, code, name, env):
		#codefile, configfile, oldcodefile = snafulib.snafu.SnafuImport.importfunction(actioninfo["name"], None, x, False)
		codefile = os.path.join(snafulib.snafu.SnafuImport.functiondir, filename)
		f = open(codefile, "w")
		f.write(code)
		print("+ code: {}".format(codefile))

	def export_snafu_zip(self, filename, code, name, env, config=None, convert=False):
		codefile, configfile, oldcodefile = snafulib.snafu.SnafuImport.importfunction(name, filename, config, convert)
		print("+ code: {}".format(codefile))
		print("+ configuration: {}".format(configfile))
		if oldcodefile:
			print("+ converted; old code: {}".format(oldcodefile))

	def archivedfile(self, filename):
		td = os.path.join(self.td.name, str(uuid.uuid4()))
		os.makedirs(td, exist_ok=True)
		cwd = os.getcwd()
		subprocess.run("cd {} && unzip -o -q {}".format(td, os.path.join(cwd, filename)), shell=True)
		codefiles = glob.glob(os.path.join(td, "*.py"))
		if len(codefiles) == 0:
			codefiles = glob.glob(os.path.join(td, "*.java"))
		if len(codefiles) == 0:
			codefiles = glob.glob(os.path.join(td, "*.class"))
		if len(codefiles) == 0:
			codefiles = glob.glob(os.path.join(td, "*.js"))
		return codefiles

	def export_funktion(self, filename, code, name, env):
		if not code:
			codefiles = self.archivedfile(filename)
			if len(codefiles) == 1:
				filename = codefiles[0]
				code = open(filename).read()
			else:
				print("- skip archive: ambiguous contents ({})".format(codefiles))
				return
		codeline = code.replace("\n", "\\n")
		subprocess.run("funktion create fn -n '{}' -s '{}'".format(name, codeline), shell=True)
		print("+ code: {} (in funktion)".format(os.path.basename(filename)))

	def export_fission(self, filename, code, name, env):
		if not code:
			codefiles = self.archivedfile(filename)
			if len(codefiles) == 1:
				filename = codefiles[0]
				code = open(filename).read()
			else:
				print("- skip archive: ambiguous contents ({})".format(codefiles))
				return
		f = tempfile.NamedTemporaryFile()
		f.write(bytes(code, "utf-8"))
		f.flush()
		codefile = f.name
		subprocess.run("fission function create --name '{}' --env {} --code '{}'".format(name, env, codefile), shell=True)
		print("+ code: {} (in fission)".format(os.path.basename(filename)))

	def export_kubeless(self, filename, code, name, env):
		if not code:
			codefiles = self.archivedfile(filename)
			if len(codefiles) == 1:
				filename = codefiles[0]
				code = open(filename).read()
			else:
				print("- skip archive: ambiguous contents ({})".format(codefiles))
				return
		f = tempfile.NamedTemporaryFile()
		f.write(bytes(code, "utf-8"))
		f.flush()
		codefile = f.name
		mangledname = name.replace(" ", "-").lower()
		handler = os.path.basename(codefile) + ".main"
		subprocess.run("kubeless function deploy '{}' --runtime {} --handler '{}' --from-file '{}' --trigger-http".format(mangledname, env, handler, codefile), shell=True)
		print("+ code: {} (in kubeless)".format(os.path.basename(filename)))

	def import_openwhisk(self, target):
		proc = subprocess.run("wsk list", stdout=subprocess.PIPE, shell=True)
		out = proc.stdout.decode("utf-8")
		inactions = False
		for line in out.split("\n"):
			line = line.split(" " * 2)
			if line[0] == "actions":
				inactions = True
			elif line[0] == "triggers":
				inactions = False
			elif inactions:
				function = line[0]
				print("import", function)
				proc = subprocess.run("wsk action get '{}'".format(function), stdout=subprocess.PIPE, shell=True)
				out = proc.stdout.decode("utf-8")
				out = out[out.find("\n"):]
				#print("CODE", out)
				actioninfo = json.loads(out)
				code = actioninfo["exec"]
				filename = None
				env = None
				if code["kind"] == "nodejs" or code["kind"] == "nodejs:6":
					filename = actioninfo["name"] + ".js"
					env = "nodejs"
				elif code["kind"] == "python" or code["kind"] == "python:2":
					filename = actioninfo["name"] + ".py"
					env = "python"
				else:
					print("- skip ({})".format(code["kind"]))

				if filename:
					if target == "snafu":
						self.export_snafu(filename, code["code"], actioninfo["name"], env)
					elif target == "funktion":
						self.export_funktion(filename, code["code"], actioninfo["name"], env)
					elif target == "fission":
						self.export_fission(filename, code["code"], actioninfo["name"], env)
					elif target == "kubeless":
						self.export_kubeless(filename, code["code"], actioninfo["name"], env)

	def import_gfunctions(self, target):
		proc = subprocess.run("gcloud beta functions list", stdout=subprocess.PIPE, shell=True)
		out = proc.stdout.decode("utf-8")
		functiondir = snafulib.snafu.SnafuImport.functiondir
		for line in out.split("\n"):
			lineparts = line.split(" ")
			if len(lineparts) > 1 and lineparts[0] != "NAME":
				funcname = lineparts[0]
				print("import", funcname)
				snafulib.snafu.SnafuImport.functiondir = os.path.join(functiondir, funcname)
				proc = subprocess.run("gcloud beta functions describe {}".format(funcname), stdout=subprocess.PIPE, shell=True)
				out = proc.stdout.decode("utf-8")
				#sourceArchiveUrl: gs://functions-163510-bucket/function-1-2017-04-03T10:10:25.959Z.zip
				for line in out.split("\n"):
					key, *value = line.split(":")
					value = ":".join(value)
					if key == "sourceArchiveUrl":
						funccode = value.strip()
						codezip = os.path.join(snafulib.snafu.SnafuImport.functiondir, "..", os.path.basename(funccode))
						proc = subprocess.run("gsutil -q cp {} {}".format(funccode, codezip), stdout=subprocess.PIPE, shell=True)

						# FIXME: read and assign runtime
						env = "python"

						if target == "snafu":
							self.export_snafu_zip(codezip, None, funcname, env)
						elif target == "funktion":
							self.export_funktion(codezip, None, funcname, env)
						elif target == "fission":
							self.export_fission(codezip, None, funcname, env)
						elif target == "kubeless":
							self.export_kubeless(codezip, None, funcname, env)

	def import_lambda(self, target, convert):
		proc = subprocess.run("aws lambda list-functions", stdout=subprocess.PIPE, shell=True)
		out = proc.stdout.decode("utf-8")
		functions = json.loads(out)
		functiondir = snafulib.snafu.SnafuImport.functiondir
		for func in functions["Functions"]:
			funcname = func["FunctionName"]
			print("import", funcname)
			snafulib.snafu.SnafuImport.functiondir = os.path.join(functiondir, funcname)
			proc = subprocess.run("aws lambda get-function --function-name {}".format(funcname), stdout=subprocess.PIPE, shell=True)
			out = proc.stdout.decode("utf-8")
			function = json.loads(out)
			funccode = function["Code"]["Location"]
			codezip = os.path.join(snafulib.snafu.SnafuImport.functiondir, "..", funcname + ".zip")
			os.makedirs(snafulib.snafu.SnafuImport.functiondir, exist_ok=True)
			subprocess.run("wget -q -O {} '{}'".format(codezip, funccode), shell=True)

			env = None
			runtime = func["Runtime"]
			if runtime == "python2.7":
				env = "python"
			else:
				print("- skip ({})".format(runtime))

			if env:
				if target == "snafu":
					self.export_snafu_zip(codezip, None, funcname, env, func, convert)
				elif target == "funktion":
					self.export_funktion(codezip, None, funcname, env)
				elif target == "fission":
					self.export_fission(codezip, None, funcname, env)
				elif target == "kubeless":
					self.export_kubeless(codezip, None, funcname, env)

class SnafuImportRunner:
	def __init__(self):
		siu = SnafuImportUtility()
		siu.start_import()
