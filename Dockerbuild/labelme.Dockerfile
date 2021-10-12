ARG BASE_IMAGE=ubuntu:20.04
FROM $BASE_IMAGE AS base

MAINTAINER "Giacomo Nodjoumi <giacomo.nodjoumi@hyranet.info>"

ENV DEBIAN_FRONTEND=noninteractive

RUN                                           \
  apt-get update &&                           \
  apt-get install --no-install-recommends -y  \
    python3                                   \
    python3-pip                               \
    python3-matplotlib                        \  
	python3-pyqt5                             \
	pyqt5-dev-tools                           \
	qttools5-dev-tools                     && \
    pip3 --no-cache-dir install setuptools wheel PyQt5 labelme && \
    apt-get install --no-install-recommends -y \
  	qt5-image-formats-plugins                && \
    rm -rf /var/lib/apt/lists/*               


    
ARG UID=1000
ARG GID=100
ARG PASSWORD=123456
RUN useradd -m -d /home/user -u $UID -g $GID -s /bin/bash user \
    && echo "user:$PASSWORD" | chpasswd
    
WORKDIR /home/user
ADD /etc/.labelmerc /home/user/.labelmerc
#ENTRYPOINT [ "labelme" ]


