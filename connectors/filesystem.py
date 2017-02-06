import pyinotify
import threading

gcb = None

class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self, event):
		#print("Creating:", event.pathname)
		ctx = {"file": event.pathname, "action": "create"}
		gcb("lambda_handler")

	def process_IN_DELETE(self, event):
		#print("Removing:", event.pathname)
		ctx = {"file": event.pathname, "action": "delete"}
		gcb("lambda_handler")

def initinternal():
	wm = pyinotify.WatchManager()
	handler = EventHandler()
	notifier = pyinotify.Notifier(wm, handler)
	mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE
	wdd = wm.add_watch("/tmp", mask, rec=True)
	notifier.loop()

def init(cb):
	global gcb
	gcb = cb

	t = threading.Thread(target=initinternal, daemon=True)
	t.start()
