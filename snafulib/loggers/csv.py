# Snafu: Snake Functions - CSV Logger

import os
import configparser

def log(source, function, duration, success, configpath):
	logurl = "snafu.csv"
	if not configpath:
		configpath = "snafu.ini"
	if os.path.isfile(configpath):
		config = configparser.ConfigParser()
		config.read(configpath)
		if "snafu" in config and "logger.csv" in config["snafu"]:
			logurl = config["snafu"]["logger.csv"]

	# FIXME: this part must become mt-safe through a protected section
	f = open(logurl, "a")
	print("{},{},{:1.3f},{}".format(source, function, duration, success), file=f)
	f.close()
