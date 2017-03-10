# build >> sudo docker build -t snafu .
# run   >> sudo docker run -p 10000:10000 -ti snafu

FROM python:3

ADD . /opt

RUN echo 'cd /opt && PYTHONPATH=/usr/lib/python3/dist-packages python3 -u ./snafu-control $*' > /opt/snafu-control.sh && chmod +x /opt/snafu-control.sh

RUN apt-get update && apt-get install -y python3-flask python3-requests

RUN echo "deb http://deb.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y docker.io

EXPOSE 10000

CMD ["/bin/bash", "/opt/snafu-control.sh"]
