# Snafu: Snake Functions - SQLite Logger

import sqlite3
import os
import configparser

def log(source, function, duration, success):
	logurl = "/tmp/snafu.sqlite"
	if os.path.isfile("snafu.ini"):
		config = configparser.ConfigParser()
		config.read("snafu.ini")
		if "snafu" in config and "logger.sqlite" in config["snafu"]:
			logurl = config["snafu"]["logger.sqlite"]

	init = False
	if not os.path.isfile(logurl):
		init = True
	conn = sqlite3.connect(logurl)
	c = conn.cursor()
	if init:
		c.execute("CREATE TABLE log (source text, function text, duration real, success bool)")
	c.execute("INSERT INTO log (source, function, duration, success) VALUES ('{}', '{}', {}, '{}')".format(source, function, duration, success))
	conn.commit()
	conn.close()
