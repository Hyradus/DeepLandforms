ARG BASE_IMAGE=nvidia/cuda:11.3.0-cudnn8-runtime-ubuntu20.04
FROM $BASE_IMAGE AS jupyter-base

MAINTAINER "Giacomo Nodjoumi <giacomo.nodjoumi@hyranet.info>"

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and its tools
RUN apt update && apt install --no-install-recommends -y 	\
    git 							\
    build-essential 				\
    curl 							\
    libgl1-mesa-dev 				\
    libglib2.0-0 					\
    python3.9-dev 					\
    python3.9-distutils 			&& \
    rm -rf /var/lib/apt/lists/*	    && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
	python3.9 get-pip.py 									&& \
	pip3 -q install pip --upgrade  && \
    pip3 --no-cache-dir install 	\
	setuptools 						\
    jupyterlab 						\
    && rm -rf /var/lib/apt/lists/*

FROM jupyter-base AS torch

RUN pip3 --no-cache-dir install p torch==1.10.0+cu113 torchvision==0.11.1+cu113  -f https://download.pytorch.org/whl/torch_stable.html

FROM torch AS jupytorch
RUN pip3 --no-cache-dir install 	\
	colour							\
	geopandas						\
	labelme2coco					\
	matplotlib						\
	numpy 							\
	opencv-python					\
	opencv-contrib-python			\
	pandas							\
	psutil							\
	rasterio						\
	scikit-image					\
	scikit-learn					\
	scipy 							\
	tqdm							\
    && rm -rf /var/lib/apt/lists/*

FROM jupytorch AS detectron2

RUN python3.9 -m pip --no-cache-dir install 'git+https://github.com/facebookresearch/detectron2.git'

FROM detectron2 AS deeplandforms

ARG UNAME=user
ENV UNAME=$UNAME
ARG UID=1000
ARG GID=100
ARG PASSWORD=123456
ENV PASSWORD=$PASSWORD

RUN groupadd -g $GID -o $UNAME && \
        useradd -m -d /home/$UNAME -u $UID -g $GID -s /bin/bash $UNAME && \
        echo "$UNAME:$PASSWORD" | chpasswd

WORKDIR /home/$UNAME

#EXPOSE 8688

#CMD ["jupyter","lab", "--port=8688","--no-browser", "--ip=0.0.0.0"]
