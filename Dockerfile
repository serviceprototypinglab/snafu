# build >> sudo docker build -t snafu .
# debug >> sudo docker run -ti snafu bash
# run   >> sudo docker run -p 10000:10000 -ti snafu

FROM python:3

RUN echo "deb http://deb.debian.org/debian jessie-backports main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian stretch main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      python3-flask \
      python3-requests \
      docker.io \
      awscli \
      unzip \
      nodejs-legacy \
    && \
    apt-get remove -y python3-botocore && \
    rm -rf /var/lib/apt/lists/* && \
    # Dumb Init
    wget https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb && \
    dpkg -i dumb-init_1.2.0_amd64.deb && \
    # Python deps
    pip install urllib3 boto3 pyesprima && \
    rm /usr/local/lib/python3.6/site-packages/pyesprima/__init__.py && \
    # OpenShift CLI client
    wget -q https://console.appuio.ch/console/extensions/clients/linux/oc -O /usr/bin/oc && \
    chmod +x /usr/bin/oc && \
    # Google Cloud SDK
    wget -q https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && \
    tar xf google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && \
    rm -f google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && \
    cd google-cloud-sdk && \
    echo n | CLOUDSDK_PYTHON=python2 ./install.sh && \
    ln -s /google-cloud-sdk/bin/gcloud /usr/bin/ && \
    ln -s /google-cloud-sdk/bin/gsutil /usr/bin/ && \
    cd / && \
    echo y | gcloud components install beta && \
    echo "def GetTestNames(): return []" > /google-cloud-sdk/platform/gsutil/gslib/tests/util.py && \
    echo "import unittest" >> /google-cloud-sdk/platform/gsutil/gslib/tests/util.py && \
    # OpenWhisk utilities
    wget -q https://openwhisk.ng.bluemix.net/cli/go/download/linux/amd64/wsk -O /usr/bin/wsk && \
    chmod +x /usr/bin/wsk

# Add and configure Snafu
ADD . /opt
WORKDIR /opt
ENV PYTHONPATH=/usr/lib/python3/dist-packages
RUN mkdir -p ~/.aws && \
    echo "[default]\nregion = invalid" > ~/.aws/config && \
    echo "[snafu]\nlogger.csv = /opt/functions-local/.snafu.csv" > /opt/snafu.ini

EXPOSE 10000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/opt/snafu-control"]
