from setuptools import setup
import os

def findfiles(pathlist):
	for path in pathlist:
		for dirpath, dirnames, files in os.walk(path):
			for f in files:
				if not f.endswith(".pyc") and not f.endswith(".class"):
					yield os.path.join(dirpath, f)

setup(
	name="snafu",
	version="0.0.0",
	url="https://github.com/serviceprototypinglab/snafu",
	author="Josef Spillner",
	author_email="josef.spillner@zhaw.ch",
	license="Apache 2.0",
	classifiers=[
		"Development Status :: 2 - Pre-Alpha",
		"Environment :: Console",
		"Environment :: No Input/Output (Daemon)",
		"Intended Audience :: Science/Research",
		"License :: OSI Approved :: Apache Software License",
		"Programming Language :: Python :: 3",
		"Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware"
	],
	keywords="cloud faas serverless functions",
	packages=["snafulib"],
	scripts=["snafu", "snafu-import", "snafu-accounts", "snafu-control"],
	data_files=[(os.path.dirname(f), [f]) for f in findfiles(["executors", "loggers", "authenticators", "connectors"])],
	install_requires=["flask"]
	#entry_points={
	#	"console_scripts": [
	#		"snafu=snafu:main",
	#		"snafu-import=snafuimport:main",
	#		"snafu-control=snafucontrol:main",
	#		"snafu-accounts=snafuaccounts:main"
	#	]
	#}
)
