FROM python:3.7.5-buster

MAINTAINER Keisuke Yamanaka <vaivailx@gmail.com>

ENV APP_HOME /app
WORKDIR $APP_HOME
ADD . /app

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

# Configure apt and install packages
RUN echo "deb http://www.deb-multimedia.org buster main non-free" >> /etc/apt/sources.list \
    && apt-get update -oAcquire::AllowInsecureRepositories=true \
    && apt-get -y install deb-multimedia-keyring --allow-unauthenticated\
    && apt-get update \
    && apt-get -y install --no-install-recommends apt-utils dialog 2>&1 \
    && apt-get -y install ffmpeg \
    # Update Python environment based on requirements.txt
    && pip --disable-pip-version-check --no-cache-dir install -r requirements.txt \
    && rm -rf requirements.txt \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=

# Set Tokyo ID
ENV RADIKO_AREA_ID=JP13

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/radiko_recorder_account_key.json

ENV PORT '8080'
CMD python3 webapp.py
EXPOSE 8080
