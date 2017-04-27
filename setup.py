# python3 setup.py sdist
# python3 setup.py bdist_wheel
# python3 setup.py bdist_egg
# twine upload dist/*.* [-r testpypi]
# -> automated in tools/make-dist.sh

from setuptools import setup
import os

#def findfiles(pathlist):
#	for path in pathlist:
#		for dirpath, dirnames, files in os.walk(path):
#			for f in files:
#				if not f.endswith(".pyc") and not f.endswith(".class"):
#					yield os.path.join(dirpath, f)

#import sys
#base = "lib/python{}.{}/site-packages".format(sys.version_info[0], sys.version_info[1])

setup(
	name="snafu",
	description="Swiss Army Knife of Serverless Computing",
	version="0.0.0.post6",
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
	packages=["snafulib", "snafulib.executors", "snafulib.loggers", "snafulib.authenticators", "snafulib.connectors"],
	scripts=["snafu", "snafu-import", "snafu-accounts", "snafu-control"],
	#data_files=[(os.path.join(base, os.path.dirname(f)), [f]) for f in findfiles(["executors", "loggers", "authenticators", "connectors"])],
	#package_data={"snafulib": findfiles(["snafulib/executors", "snafulib/loggers", "snafulib/authenticators", "snafulib/connectors"])},
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
