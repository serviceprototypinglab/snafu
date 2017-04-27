# Snafu: Snake Functions - Filesystem Connector

import pyinotify
import threading
import os
import configparser

gcb = None
gf = None

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		event = {"file": event.pathname, "action": "create"}
		gcb(gf, event=event)

	def process_IN_DELETE(self, event):
		event = {"file": event.pathname, "action": "delete"}
		gcb(gf, event=event)

def initinternal(function, configpath):
	global gcb
	gf = function

	connecturl = None
	if not configpath:
		configpath = "snafu.ini"
	if not function:
		function = "snafu"
	if os.path.isfile(configpath):
		config = configparser.ConfigParser()
		config.read(configpath)
		if function in config and "connector.filesystem" in config[function]:
			connecturl = config[function]["connector.filesystem"]

	if connecturl:
		wm = pyinotify.WatchManager()
		handler = EventHandler()
		notifier = pyinotify.Notifier(wm, handler)
		mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE
		wdd = wm.add_watch(connecturl, mask, rec=True)
		notifier.loop()

def init(cb, function=None, configpath=None):
	global gcb
	gcb = cb

	t = threading.Thread(target=initinternal, daemon=True, args=(function, configpath))
	t.start()
