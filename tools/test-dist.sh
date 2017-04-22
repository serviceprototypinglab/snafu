#!/bin/bash

if [ -d ../dist ]
then
	cd ..
fi

if [ ! -d dist ]
then
	echo "Error: Needs to run from root directory." >&2
	exit 1
fi

python3 setup.py bdist_egg

mkdir -p dist/test-dist
virtualenv -p python3 dist/test-dist
cp dist/snafu-0.0.0-py3.5.egg dist/test-dist
cd dist/test-dist
source bin/activate
easy_install -Z snafu-0.0.0-py3.5.egg
bash
