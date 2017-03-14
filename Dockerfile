# build >> sudo docker build -t snafu .
# debug >> sudo docker run -ti snafu bash
# run   >> sudo docker run -p 10000:10000 -ti snafu

FROM python:3

ADD . /opt

RUN echo 'cd /opt && PYTHONPATH=/usr/lib/python3/dist-packages python3 -u ./snafu-control $*' > /opt/snafu-control.sh && chmod +x /opt/snafu-control.sh

RUN apt-get update && apt-get install -y python3-flask python3-requests

RUN echo "deb http://deb.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y docker.io

# non-working workaround
RUN echo "deb http://deb.debian.org/debian stretch main" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends python3-boto3 python-boto3
RUN apt-get install python-urllib3

RUN wget -q https://console.appuio.ch/console/extensions/clients/linux/oc -O /usr/bin/oc
RUN chmod +x /usr/bin/oc

EXPOSE 10000

CMD ["/bin/bash", "/opt/snafu-control.sh"]
