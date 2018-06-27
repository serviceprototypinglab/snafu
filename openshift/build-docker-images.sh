#!/bin/sh

rm -rf _snafu_clean_
git clone .. _snafu_clean_
#cd _snafu_clean_
cp Dockerfile* _snafu_clean_
docker build -t snafu -f _snafu_clean_/Dockerfile _snafu_clean_
docker build -t snafucomplete -f _snafu_clean_/Dockerfile.complete _snafu_clean_

if [ "$1" = "release" ]
then
	docker tag snafu jszhaw/snafu
	docker tag snafucomplete jszhaw/snafucomplete

	docker push jszhaw/snafu
	docker push jszhaw/snafucomplete
else
	echo "# Note: Not pushing. Run with 'release' option to push."
fi
