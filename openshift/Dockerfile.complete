# build >> (sudo) docker build -t snafucomplete -f Dockerfile.complete . # -> now use: build-docker-images.sh
# debug >> (sudo) docker run -ti snafucomplete bash
# run   >> (sudo) docker run -p 10000:10000 -ti snafucomplete

FROM jszhaw/snafu

RUN \
    # AWS CLI client / Docker CLI client
    apt-get update && \
    apt-get install -y --no-install-recommends \
      awscli \
      docker.io \
    && \
    # OpenShift CLI client
    wget -q https://console.appuio.ch/console/extensions/clients/linux/oc -O /usr/bin/oc && \
    chmod +x /usr/bin/oc && \
    # Google Cloud SDK
    wget -q https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && \
    tar xf google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && \
    rm -f google-cloud-sdk-149.0.0-linux-x86_64.tar.gz && \
    cd google-cloud-sdk && \
    echo n | CLOUDSDK_PYTHON=python2 ./install.sh && \
    ln -s /opt/google-cloud-sdk/bin/gcloud /usr/bin/ && \
    ln -s /opt/google-cloud-sdk/bin/gsutil /usr/bin/ && \
    cd / && \
    echo y | gcloud components install beta && \
    echo "def GetTestNames(): return []" > /opt/google-cloud-sdk/platform/gsutil/gslib/tests/util.py && \
    echo "import unittest" >> /opt/google-cloud-sdk/platform/gsutil/gslib/tests/util.py && \
    # OpenWhisk utilities
    wget -q https://openwhisk.ng.bluemix.net/cli/go/download/linux/amd64/wsk -O /usr/bin/wsk && \
    chmod +x /usr/bin/wsk
