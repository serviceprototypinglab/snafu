#!/bin/bash

if [ -f ../setup.py ]
then
	cd ..
fi

if [ ! -f setup.py ]
then
	echo "Error: Needs to run from root directory." >&2
	exit 1
fi

rm -rf dist
python3 setup.py sdist
python3 setup.py bdist_wheel
python3 setup.py bdist_egg

read -p "Upload? (y/n)" upload
if [ "$upload" = "y" ]
then
	twine upload dist/*.*
fi
