# build >> sudo docker build -t snafu .
# debug >> sudo docker run -ti snafu bash
# run   >> sudo docker run -p 10000:10000 -ti snafu

FROM python:3

ADD . /opt

RUN echo 'cd /opt && PYTHONPATH=/usr/lib/python3/dist-packages python3 -u ./snafu-control $*' > /opt/snafu-control.sh && chmod +x /opt/snafu-control.sh

RUN apt-get update && apt-get install -y python3-flask python3-requests

RUN echo "deb http://deb.debian.org/debian jessie-backports main" >> /etc/apt/sources.list
RUN apt-get update && apt-get install -y docker.io

# non-working workaround: now boto3/urllib3 work but python2 does likely not
RUN echo "deb http://deb.debian.org/debian stretch main" >> /etc/apt/sources.list
#RUN apt-get update && apt-get install -y --no-install-recommends python3-boto3 python-boto3
#RUN apt-get install python-urllib3
RUN apt-get remove -y python3-botocore
RUN pip install urllib3 boto3
#RUN cp -r /usr/local/lib/python3.6/site-packages/urllib3/* /usr/lib/python3/dist-packages/urllib3

RUN mkdir -p ~/.aws && echo "[default]\nregion = invalid" > ~/.aws/config

RUN wget -q https://console.appuio.ch/console/extensions/clients/linux/oc -O /usr/bin/oc
RUN chmod +x /usr/bin/oc

RUN apt-get install -y --no-install-recommends awscli
RUN wget -q https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && tar xf google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && rm -f google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && cd google-cloud-sdk && echo n | CLOUDSDK_PYTHON=python2 ./install.sh
RUN ln -s /google-cloud-sdk/bin/gcloud /usr/bin/
RUN echo y | gcloud components install beta

EXPOSE 10000

CMD ["/bin/bash", "/opt/snafu-control.sh"]
