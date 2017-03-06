# Snafu: Snake Functions - CSV Logger

def log(source, function, duration, success):
	# FIXME: this part must become mt-safe through a protected section
	f = open("snafu.csv", "a")
	print("{},{},{:1.3f},{}".format(source, function, duration, success), file=f)
	f.close()
