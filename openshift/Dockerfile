# prep  >> git status --ignored --porcelain
# build >> (sudo) docker build -t snafu . # -> now use: build-docker-images.sh
# debug >> (sudo) docker run -ti snafu bash
# run   >> (sudo) docker run -p 10000:10000 -ti snafu

FROM python:3

RUN echo "deb http://deb.debian.org/debian jessie-backports main" >> /etc/apt/sources.list && \
    echo "deb http://deb.debian.org/debian stretch main" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      python3-flask \
      python3-requests \
      unzip \
      nodejs-legacy \
    && \
    apt-get remove -y python3-botocore && \
    apt-get clean && \
    ##rm -rf /var/lib/apt/lists/* && \
    # Python deps
    pip install urllib3 boto3 pyesprima && \
    rm /usr/local/lib/python3.6/site-packages/pyesprima/__init__.py && \
    # Dumb Init
    wget https://github.com/Yelp/dumb-init/releases/download/v1.2.0/dumb-init_1.2.0_amd64.deb && \
    dpkg -i dumb-init_1.2.0_amd64.deb

# Workaround due to apt-get install python3-pyinotify leading to stalled systemd triggers
RUN pip install pyinotify

# Add and configure Snafu
ADD . /opt
WORKDIR /opt
ENV PYTHONPATH=/usr/lib/python3/dist-packages
RUN mkdir -p ~/.aws && \
    echo "[default]\nregion = invalid" > ~/.aws/config && \
    echo "[snafu]\nlogger.csv = /opt/functions-local/.snafu.csv" > /opt/snafu.ini

COPY integration/snafu.service /etc/systemd/system/

EXPOSE 10000

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/opt/snafu-control"]
