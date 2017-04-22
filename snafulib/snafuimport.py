# Snafu: Snake Functions - Import Utility Module

import argparse
import subprocess
import json
import os
import sys
import snafulib.snafu
import tempfile

class SnafuImportUtility:
	def __init__(self):
		pass

	def start_import(self):
		parser = argparse.ArgumentParser(description="Snake Functions as a Service - Import Utility")
		parser.add_argument("-s", "--source", help="import source", choices=["lambda", "gfunctions", "openwhisk"], default=None)
		parser.add_argument("-t", "--target", help="import target", choices=["snafu", "funktion", "fission"], default="snafu")
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
						#codefile, configfile, oldcodefile = snafulib.snafu.SnafuImport.importfunction(actioninfo["name"], None, x, False)
						codefile = os.path.join(snafulib.snafu.SnafuImport.functiondir, filename)
						f = open(codefile, "w")
						f.write(code["code"])
						print("+ code: {}".format(codefile))
					elif target == "funktion":
						codeline = code["code"].replace("\n", "\\n")
						subprocess.run("funktion create fn -n '{}' -s '{}'".format(actioninfo["name"], codeline), shell=True)
					elif target == "funktion":
						f = tempfile.NamedTemporaryFile()
						f.write(code["code"])
						f.flush()
						codefile = f.name
						subprocess.run("fission function create --name '{}' --env {} --code '{}'".format(actioninfo["name"], env, codefile), shell=True)

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

						codefile, configfile, oldcodefile = snafulib.snafu.SnafuImport.importfunction(funcname, codezip, None, False)
						print("+ code: {}".format(codefile))

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
			subprocess.run("wget -q -O {} '{}'".format(codezip, funccode), shell=True)

			codefile, configfile, oldcodefile = snafulib.snafu.SnafuImport.importfunction(funcname, codezip, func, convert)

			print("+ code: {}".format(codefile))
			print("+ configuration: {}".format(configfile))
			if oldcodefile:
				print("+ converted; old code: {}".format(oldcodefile))

class SnafuImportRunner:
	def __init__(self):
		siu = SnafuImportUtility()
		siu.start_import()
