FROM python:3.7.5-buster

MAINTAINER Keisuke Yamanaka <vaivailx@gmail.com>

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
    && pip --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=
# Copy file

# Set Tokyo ID
ENV RADIKO_AREA_ID=JP13

CMD ["python", "record_radiko.py", "LFR", "nishikawa_chokonaipon", "10"]