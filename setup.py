from setuptools import setup
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
	packages=["snafu"],
	entry_points={
		"console_scripts": [
			"snafu=snafu:main",
			"snafu-import=snafuimport:main",
			"snafu-control=snafucontrol:main",
			"snafu-accounts=snafuaccounts:main"
		]
	}
)
