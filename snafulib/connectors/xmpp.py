# Snafu: Snake Functions - XMPP Connector
# (derived from basexmppbot.py / ported to python3-nbxmpp)

import nbxmpp
import time
import configparser
import os
#import threading
import urllib.parse

from gi.repository import GObject as gobject

class BaseXMPPBot:
	def __init__(self, botname, jid, password, target, debug=True):
		self.initinternal(botname, jid, password, target)

		self.readystep = 0
		self.debug = debug
		self.lasttime = 0

	def initinternal(self, botname, jid, password, target):
		self.botname = botname
		self.jid = jid
		self.password = password
		self.target = target

	def presenceHandler(self, conn, presence_node):
		if self.debug:
			print(":: xmpp presence")

	def iqHandler(self, conn, iq_node):
		if self.debug:
			print(":: xmpp iq")

		reply = iq_node.buildReply('result')
		conn.send(reply)
		raise nbxmpp.NodeProcessed

	def messageHandler(self, conn, mess_node):
		if self.debug:
			print(":: xmpp handler", "[" + str(mess_node.getFrom()) + "]", mess_node.getBody())

		if self.readystep == 0:
			self.readystep = 1

		if "messageroutine" in dir(self):
			self.messageroutine(str(mess_node.getFrom()), str(mess_node.getBody()))

	def on_auth(self, con, auth):
		if not auth:
			if self.debug:
				print(":: xmpp could not authenticate!")
			return
		if self.debug:
			print(":: xmpp authenticated using " + auth)

		self.client.RegisterHandler('presence', self.presenceHandler)
		self.client.RegisterHandler('iq', self.iqHandler)
		self.client.RegisterHandler('message', self.messageHandler)

		self.client.sendPresence()
		if self.target:
			self.client.sendPresence(self.target + "/" + self.botname)

	def get_password(self, cb, mech):
		cb(self.password)

	def on_connect(self, con, con_type):
		if self.debug:
			print(":: xmpp connected", con, con_type)
		auth = self.client.auth(self.jidproto.getNode(), self.password, resource=self.jidproto.getResource(), sasl=1, on_auth=self.on_auth)

	def on_failure(self):
		if self.debug:
			print(":: xmpp connection failed")

	def connect(self):
		self.readystep = 0

		self.client_cert = None
		self.sm = nbxmpp.Smacks(self)

		self.jidproto = nbxmpp.protocol.JID(self.jid)
		self.client = nbxmpp.NonBlockingClient(self.jidproto.getDomain(), nbxmpp.idlequeue.get_idlequeue(), caller=self)
		self.client.connect(self.on_connect, self.on_failure, secure_tuple=('tls', '', '', None, None))

	def _event_dispatcher(self, realm, event, data):
		if self.debug:
			print(":: xmpp dispatcher >> realm:", realm, "event:", type(event), event, "data:", type(data), data)
		pass

	def worksafely(self):
		self.connect()
		ml = gobject.MainLoop()
		ml.run()

	def post(self, msg):
		self.client.send(nbxmpp.protocol.Message(self.target, msg, "groupchat"))

class Connector(BaseXMPPBot):
	def __init__(self, connectconfig, debug):
		u = urllib.parse.urlparse(connectconfig)
		password = u.password
		jid = u.username + "@" + u.hostname

		target = None
		botname = None
		BaseXMPPBot.__init__(self, botname, jid, password, target, debug=debug)

	def messageroutine(self, sender, msg):
		if self.debug:
			print(":: (xmpp connector) message received...", msg)

		response = gcb(msg)
		rmsg = self.client.send(nbxmpp.protocol.Message(sender, response, typ="chat"))

def initinternal(function, configpath):
	debug = True

	connectconfig = None
	if not configpath:
		configpath = "snafu.ini"
	if not function:
		function = "snafu"
	if os.path.isfile(configpath):
		config = configparser.ConfigParser()
		config.read(configpath)
		if function in config and "connector.xmpp" in config[function]:
			connectconfig = config[function]["connector.xmpp"]

	if debug:
		print(":: (xmpp url)", connectconfig)

	if connectconfig:
		connector = Connector(connectconfig, debug)
		connector.worksafely()

def init(cb, function=None, configpath=None):
	global gcb
	gcb = cb

	#t = threading.Thread(target=initinternal, daemon=True, args=(function, configpath))
	#t.start()
	initinternal(function, configpath)
