# Snafu: Snake Functions - CSV Logger

def log(source, function, duration, success):
	logurl = "snafu.csv"
	if os.path.isfile("snafu.ini"):
		config = configparser.ConfigParser()
		config.read("snafu.ini")
		if "snafu" in config and "log.csv" in config["snafu"]:
			logurl = config["snafu"]["log.csv"]

	# FIXME: this part must become mt-safe through a protected section
	f = open(logurl, "a")
	print("{},{},{:1.3f},{}".format(source, function, duration, success), file=f)
	f.close()
