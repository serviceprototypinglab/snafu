rm -rf _snafu_clean_
git clone .. _snafu_clean_
#cd _snafu_clean_
cp Dockerfile* _snafu_clean_
docker build -t snafu -f _snafu_clean_/Dockerfile _snafu_clean_
docker build -t snafucomplete -f _snafu_clean_/Dockerfile.complete _snafu_clean_
