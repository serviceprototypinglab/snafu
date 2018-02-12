# Snafu: Snake Functions - Control Plane Module

import flask
import json
import argparse
import os
import base64
import subprocess
import glob
import snafulib.snafu
import logging
import importlib
import threading
import time
import shutil

"""
AWS CLI support
Legend: * = implemented, / = noop, # = not necessary
* [s3] "download-function"
/ [sts] get-caller-identity
/ add-permission
create-alias
create-event-source-mapping
* create-function
delete-alias
delete-event-source-mapping
* delete-function
get-account-settings
get-alias
get-event-source-mapping
* get-function
* get-function-configuration
get-policy
# help
* invoke
invoke-async
list-aliases
list-event-source-mappings
* list-functions
list-versions-by-function
publish-version
remove-permission
update-alias
update-event-source-mapping
* update-function-code
* update-function-configuration

GCloud CLI support
Legend: * = implemented, / = noop, # = not necessary
(*) call
delete
deploy
describe
* list

WSK CLI support
Legend: * = implemented, / = noop, # = not necessary
/ namespace list
(*) list
(*) action list
(*) action get
(*) action invoke
"""

class ControlUtil:
	def createconfig(function, sourceinfos):
		sourcename, functionname = function.split(".")

		fmap = {}
		env = {}
		envvars = {}
		if envvars:
			env["Variables"] = envvars
		vpc = {}
		#vpc["SecurityGroupIds"] = []
		#vpc["SubnetIds"] = []
		fmap["FunctionName"] = function
		fmap["Version"] = "$LATEST"
		#fmap["MemorySize"] = 128
		fmap["MemorySize"] = -1
		fmap["Handler"] = "{}.{}".format(sourcename, functionname)
		fmap["LastModified"] = "2017-01-01T00:00:00.000+0000"
		fmap["CodeSha256"] = sourceinfos.checksum
		fmap["CodeSize"] = sourceinfos.size
		fmap["Timeout"] = 3
		#fmap["Runtime"] = "python2.7"
		fmap["Runtime"] = "python3"
		fmap["Description"] = "<function without configuration>"
		#fmap["Role"] = "arn:...:XXX"
		#fmap["FunctionArn"] = "arn:...:XXX"
		if env:
			fmap["Environment"] = env
		if vpc:
			fmap["VpcConfig"] = vpc
		return fmap

	def functionconfiguration(function):
		func, config, sourceinfos = SnafuControl.snafu.functions[function]
		if config:
			fmap = config
		else:
			fmap = ControlUtil.createconfig(function, sourceinfos)
		return fmap

	def notauthorised():
		err = json.dumps({"errorMessage": "NotAuthenticated"})
		return err, 501

	def reaperthread(debug=False):
		if debug:
			print("REAPER init")
		f = open("/proc/net/tcp")
		while True:
			time.sleep(1)
			try:
				ControlUtil.reaperthread_internal(True, f)
			except Exception as e:
				if debug:
					print("REAPER crash {}".format(e))

	def deployerthread(snafu, debug=False):
		if debug:
			print("DEPLOYER init")
		import pyinotify
		wm = pyinotify.WatchManager()
		mask = pyinotify.IN_CREATE

		class EventHandler(pyinotify.ProcessEvent):
			def process_IN_CREATE(self, event):
				print("Hot deployment of function {}".format(event.pathname))
				snafu.activate([event.pathname], "any")

		handler = EventHandler()
		notifier = pyinotify.Notifier(wm, handler)
		wdd = wm.add_watch("functions-local", mask, rec=True)
		notifier.loop()

	def reaperthread_internal(debug, f):
		if debug:
			print("REAPER reap")
		fds = glob.glob("/proc/{}/fd/*".format(os.getpid()))
		sockets = {}
		for fd in fds:
			try:
				rp = os.path.realpath(fd)
				if os.path.islink(fd) and not os.path.exists(rp):
					socket = int(os.path.basename(fd))
					if debug:
						print("+", socket, rp)
					rp = os.path.basename(rp).replace("socket:[", "").replace("]", "")
					sockets[rp] = socket
			except:
				if debug:
					print("-", fd)
				pass
		f.seek(0)
		tcp = f.readlines()
		for line in tcp:
			line = [x for x in line.split(" ") if x]
			st = line[3]
			inode = line[9]
			if inode in sockets:
				if debug:
					print("?", inode, st)
				if st == "08":
					if debug:
						print("! close", sockets[inode])
					else:
						print("Reap dangling connection {}".format(sockets[inode]))
					try:
						os.close(sockets[inode])
					except:
						pass

	def reaper():
		t = threading.Thread(target=ControlUtil.reaperthread, args=(False,))
		t.setDaemon(True)
		t.start()

	def deployer(snafu):
		t = threading.Thread(target=ControlUtil.deployerthread, args=(snafu, False))
		t.setDaemon(True)
		t.start()

class SnafuControl:
	app = flask.Flask("snafu-control")
	port = None
	snafu = None
	authenticatormods = []
	passive = False

	def __init__(self):
		pass

	@app.route("/<user>-<namespace>-<number>", methods=["HEAD", "PUT"])
	def s3(user, namespace, number):
		#if flask.request.method == "HEAD":
		#	return "{}", 404
		return "{}"

	@app.route("/<bucket>/<dir>/<objectname>.meta.json")
	def s3meta(bucket, dir, objectname):
		return "{\"python_ver\": \"3.5\"}"

	@app.route("/", methods=["POST"])
	def sts_iam():
		if "Action" in flask.request.form:
			action = flask.request.form["Action"]
			if action == "GetCallerIdentity":
				return "<GetCallerIdentityResponse xmlns='https://sts.amazonaws.com/doc/2011-06-15/'><GetCallerIdentityResult><Account>000000000000</Account></GetCallerIdentityResult></GetCallerIdentityResponse>"
			elif action == "CreateRole":
				return "<CreateRoleResponse xmlns='https://iam.amazonaws.com/doc/2010-05-08/'><CreateRoleResult><Role></Role></CreateRoleResult></CreateRoleResponse>"
			elif action == "PutRolePolicy":
				return "<PutRolePolicyResponse xmlns='https://iam.amazonaws.com/doc/2010-05-08/'></PutRolePolicyResponse>"
			else:
				err = json.dumps({"errorMessage": "UndefinedAction"})
				return err, 501

	@app.route("/api/v1/namespaces")
	def listnamespaceopenwhisk():
		d = ["snafu"]
		return json.dumps(d)

	@app.route("/api/v1/namespaces/<namespace>/")
	def listfunctionsopenwhisk(namespace):
		overridenamespace = "snafu"
		f = []
		for function in SnafuControl.snafu.functions:
			ann = [{"key": "exec", "value": "python:2"}]
			fmap = {"namespace": overridenamespace, "name": function, "annotations": ann}
			f.append(fmap)
		d = {"actions": f}
		return json.dumps(d)

	@app.route("/api/v1/namespaces/<namespace>/actions")
	# ?limit=30&skip=0
	def listfunctionsactionsopenwhisk(namespace):
		overridenamespace = "snafu"
		f = []
		for function in SnafuControl.snafu.functions:
			fmap = {"namespace": overridenamespace, "name": function}
			f.append(fmap)
		return json.dumps(f)

	@app.route("/api/v1/namespaces/<namespace>/actions/<function>")
	def getfunctionopenwhisk(namespace, function):
		overridenamespace = "snafu"
		d = {"namespace": overridenamespace, "name": function, "version": "0.0.1", "publish": False}
		return json.dumps(d)

	@app.route("/api/v1/namespaces/<namespace>/actions/<function>", methods=["POST"])
	# ?blocking=true&result=true
	def invokeopenwhisk(namespace, function):
		if SnafuControl.passive:
			return ControlUtil.notauthorised()
		data = flask.request.data.decode("utf-8")
		dataargs = json.loads(data)
		#print("F", function, dataargs)
		response = SnafuControl.snafu.execute(function, **dataargs)
		#print("R", response)
		if type(response) == dict:
			response = json.dumps(response)
		return response

	@app.route("/v1beta2/projects/<project>/locations/<location>/functions")
	# alt=json&pageSize=100
	def listfunctionsgoogle(project, location):
		f = []
		for function in SnafuControl.snafu.functions:
			fmap = {"name": function, "status": "ready", "httpsTrigger": {"url": "..."}}
			f.append(fmap)

		functions = {"functions" : f}
		return json.dumps(functions)

	@app.route("/v1beta2/projects/<project>/locations/<location>/functions/<function>", methods=["POST"])
	def invokegoogle(project, location, function):
		if SnafuControl.passive:
			return ControlUtil.notauthorised()
		function = function.split(":")[0]
		response = SnafuControl.snafu.execute(function)
		return json.dumps(response)

	@app.route("/function-download/<function>.zip")
	def functiondownload(function):
		func, config, sourceinfos = SnafuControl.snafu.functions[function]
		try:
			path = sourceinfos.source
			mode = "r"
			dirname = os.path.dirname(sourceinfos.source)
			pdirname = os.path.dirname(os.path.abspath(os.path.join(sourceinfos.source, "..")))
			zippath = os.path.join(pdirname, os.path.basename(dirname) + ".zip")
			if os.path.isfile(zippath):
				path = zippath
				mode = "rb"

			content = open(path, mode).read()
		except:
			err = json.dumps({"errorMessage": "NoZipFilePresent"})
			return err, 501
		return flask.Response(content, mimetype="application/octet-stream")

	@app.route("/2015-03-31/functions", methods=["POST"])
	def createfunction():
		auth = SnafuControl.authorise()
		if not auth:
			return ControlUtil.notauthorised()

		data = flask.request.data.decode("utf-8")
		config = json.loads(data)
		functionname = config["FunctionName"]

		if auth[1]:
			snafulib.snafu.SnafuImport.functiondir = "functions-tenants/{}/{}".format(auth[1], functionname)
		else:
			snafulib.snafu.SnafuImport.functiondir = "functions-local/{}".format(functionname)

		try:
			#os.makedirs(snafulib.snafu.SnafuImport.functiondir)
			snafulib.snafu.SnafuImport.prepare()
		except:
			err = json.dumps({"errorMessage": "ResourceConflictException"})
			return err, 501

		codezip = "{}.zip".format(snafulib.snafu.SnafuImport.functiondir)
		f = open(codezip, "wb")
		f.write(base64.b64decode(config["Code"]["ZipFile"]))
		f.close()

		del config["Code"]
		### TODO: extend configuration

		#snafulib.snafu.SnafuImport.prepare()
		snafulib.snafu.SnafuImport.importfunction(functionname, codezip, config, convert=True)

		SnafuControl.snafu.activate([snafulib.snafu.SnafuImport.functiondir], "lambda")

		return json.dumps(config)

	@app.route("/2015-03-31/functions/")
	def listfunctions():
		auth = SnafuControl.authorise()
		if not auth:
			return ControlUtil.notauthorised()

		f = []
		for function in SnafuControl.snafu.functions:
			fmap = ControlUtil.functionconfiguration(function)
			f.append(fmap)

		functions = {"Functions" : f}
		return json.dumps(functions)

	@app.route("/2015-03-31/functions/<function>", methods=["GET", "DELETE"])
	def getfunction(function):
		auth = SnafuControl.authorise()
		if not auth:
			return ControlUtil.notauthorised()

		if function in SnafuControl.snafu.functions:
			if flask.request.method == "GET":
				funccode = {}
				funccode["RepositoryType"] = "snafu"
				funccode["Location"] = "http://localhost:{}/function-download/{}.zip".format(SnafuControl.port, function)
				func = {}
				func["Code"] = funccode
				func["Configuration"] = ControlUtil.functionconfiguration(function)
				return json.dumps(func)
			elif flask.request.method == "DELETE":
				if auth[1]:
					functiondir = "functions-tenants/{}/{}".format(auth[1], function)
				else:
					functiondir = "functions-local/{}".format(function)

				if os.path.isdir(functiondir):
					shutil.rmtree(functiondir)
					if os.path.isfile(functiondir + ".zip"):
						os.remove(functiondir + ".zip")
					return json.dumps({})
				else:
					err = json.dumps({"errorMessage": "ResourceNotFoundException"})
					return err, 501
		else:
			err = json.dumps({"errorMessage": "ResourceNotFoundException"})
			return err, 501

	@app.route("/2015-03-31/functions/<function>/code", methods=["PUT"])
	def putfunctioncode(function):
		auth = SnafuControl.authorise()
		if not auth:
			return ControlUtil.notauthorised()

		if function in SnafuControl.snafu.functions:
			data = flask.request.data.decode("utf-8")
			update = json.loads(data)

			if auth[1]:
				snafulib.snafu.SnafuImport.functiondir = "functions-tenants/{}/{}".format(auth[1], function)
			else:
				snafulib.snafu.SnafuImport.functiondir = "functions-local/{}".format(function)

			codezip = "{}.zip".format(snafulib.snafu.SnafuImport.functiondir)
			f = open(codezip, "wb")
			f.write(base64.b64decode(update["ZipFile"]))
			f.close()

			snafulib.snafu.SnafuImport.importfunction(function, codezip, None)
			func, config, sourceinfos = SnafuControl.snafu.functions[function]
			#fmap = ControlUtil.functionconfiguration(function)
			# FIXME: update config, sourceinfos.checksum, sourceinfos.size
			return json.dumps(config)
		else:
			err = json.dumps({"errorMessage": "ResourceNotFoundException"})
			return err, 501

	@app.route("/2015-03-31/functions/<function>/configuration", methods=["GET", "PUT"])
	def getputfunctionconfiguration(function):
		auth = SnafuControl.authorise()
		if not auth:
			return ControlUtil.notauthorised()
		if SnafuControl.passive:
			return ControlUtil.notauthorised()

		if function in SnafuControl.snafu.functions:
			if flask.request.method == "GET":
				return json.dumps(ControlUtil.functionconfiguration(function))
			elif flask.request.method == "PUT":
				data = flask.request.data.decode("utf-8")
				update = json.loads(data)
				fmap = ControlUtil.functionconfiguration(function)
				for key in update:
					fmap[key] = update[key]
				snafulib.snafu.SnafuImport.importfunction(function, None, fmap)
				return json.dumps(fmap)
		else:
			err = json.dumps({"errorMessage": "ResourceNotFoundException"})
			return err, 501

	@app.route("/2015-03-31/functions/<function>/policy", methods=["POST"])
	def addpermission(function):
		auth = SnafuControl.authorise()
		if not auth:
			return ControlUtil.notauthorised()
		if SnafuControl.passive:
			return ControlUtil.notauthorised()

		data = flask.request.data.decode("utf-8")
		"""
		{"Action": "lambda:InvokeFunction", "StatementId": "Y_reverse", "Principal": "X"}
		->
		{"Statement": "{\"Sid\":\"Y_reverse\",\"Resource\":\"arn:aws:lambda:us-west-1:*:function:Y\",\"Effect\":\"Allow\",\"Principal\":{\"AWS\":\"arn:aws:iam::*:role/lambda_basic_execution\"},\"Action\":[\"lambda:InvokeFunction\"]}"}
		"""
		return "{}"

	@app.route("/2015-03-31/functions/<function>/invocations", methods=["POST"])
	def invoke(function):
		auth = SnafuControl.authorise()
		if not auth:
			return ControlUtil.notauthorised()
		if SnafuControl.passive:
			return ControlUtil.notauthorised()

		if SnafuControl.snafu.executormods[0].__name__ == "snafulib.executors.docker":
			response = SnafuControl.snafu.executormods[0].executecontrol(flask.request, auth[1])
		else:
			dataargs = {}
			data = flask.request.data.decode("utf-8")
			if data:
				dataargs["event"] = json.loads(data)

			response = SnafuControl.snafu.execute(function, **dataargs)

		if not response:
			#flask.abort(500)
			err = json.dumps({"errorMessage": "ServiceException"})
			return err, 501
		if type(response) == dict:
			response = json.dumps(response)
		return response

	@app.errorhandler(404)
	def notfound(error):
		return "Invalid request.", 404

	def authorise():
		if len(SnafuControl.authenticatormods) == 0:
			return True, None

		for authenticatormod in SnafuControl.authenticatormods:
			auth = authenticatormod.authorise(flask.request)
			if auth:
				if not SnafuControl.snafu.quiet:
					print("Authorised: {}".format(auth))
				return True, auth

		return False

	def setupauthenticators(self, authenticators, quiet=False):
		if "none" in authenticators:
			return

		if not quiet:
			for authenticator in authenticators:
				print("+ authenticator:", authenticator)

		SnafuControl.authenticatormods = []
		for authenticator in authenticators:
			mod = importlib.import_module("snafulib.authenticators." + authenticator)
			SnafuControl.authenticatormods.append(mod)

	def run(self):
		parser = argparse.ArgumentParser(description="Snake Functions as a Service - Control Plane")
		snafulib.snafu.SnafuRunner.add_common_arguments(parser)
		#parser.add_argument("-i", "--isolation", help="isolate stateful function instances", action="store_true")
		parser.add_argument("-a", "--authenticator", help="function authenticators; 'none' by default", choices=["aws", "none"], default=["none"], nargs="+")
		parser.add_argument("-p", "--port", help="HTTP port number", type=int, default=10000)
		parser.add_argument("-r", "--reaper", help="closed connection reaper", action="store_true")
		parser.add_argument("-d", "--deployer", help="automated hot deployment", action="store_true")
		parser.add_argument("-P", "--passive", help="passive mode without function execution", action="store_true")

		for action in parser._actions:
			if action.dest == "executor":
				action.choices.append("docker")
				action.choices.append("proxy")
				action.choices.append("openshift")

		args = parser.parse_args()

		ignore = False
		if not args.file:
			args.file.append("functions")
			args.file.append("functions-local")
			args.file.append("functions-tenants")
			ignore = True

		SnafuControl.snafu = snafulib.snafu.Snafu(args.quiet)
		SnafuControl.port = args.port
		SnafuControl.passive = args.passive
		# FIXME: should now provide the choice between lambda, gfunctions and openwhisk depending on modular activation

		self.snafu.configpath = args.settings
		self.snafu.setupparsers(snafulib.snafu.selectparsers(args.function_parser))
		self.snafu.activate(args.file, "lambda", ignore=ignore)
		self.snafu.setuploggers(args.logger)
		self.snafu.setupexecutors(snafulib.snafu.selectexecutors(args.executor))
		self.setupauthenticators(args.authenticator, args.quiet)

		if args.quiet:
			log = logging.getLogger("werkzeug")
			log.setLevel(logging.ERROR)

		if args.reaper:
			print("+ reaper")
			ControlUtil.reaper()

		if args.deployer:
			print("+ deployer")
			ControlUtil.deployer(SnafuControl.snafu)

		context = None
		if args.port == 443 or args.port == 10443:
			print("+ tls activation")
			#import flask_sslify
			#sslify = flask_sslify.SSLify(self.app)
			import ssl
			context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
			context.load_cert_chain('yourserver.crt', 'yourserver.key')
			#context="adhoc"

		self.app.run(host="0.0.0.0", port=args.port, threaded=True, ssl_context=context)

class SnafuControlRunner:
	def __init__(self):
		try:
			import setproctitle
			setproctitle.setproctitle("snafu-control")
		except:
			pass

		sc = SnafuControl()
		sc.run()
