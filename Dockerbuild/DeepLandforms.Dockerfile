<<<<<<< HEAD
ARG BASE_IMAGE=nvidia/cuda:11.7.0-runtime-ubuntu22.04
FROM $BASE_IMAGE AS jupyter-base
=======

FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
>>>>>>> 42e5c4e (Major rework, added new notebooks (YOLOv8))

MAINTAINER "Giacomo Nodjoumi <giacomo.nodjoumi@hyranet.info>"

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and its tools
RUN apt update && apt install --no-install-recommends -y 	\
    git 							\
    build-essential 				\
    curl 							\
    libgl1-mesa-dev 				\
<<<<<<< HEAD
    libglib2.0-0 					\
=======
    libglib2.0-0 					\    
>>>>>>> 42e5c4e (Major rework, added new notebooks (YOLOv8))
    python3.10-dev 					\
    python3.10-distutils 			&& \
    rm -rf /var/lib/apt/lists/*	    && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
	python3.10 get-pip.py 									&& \
<<<<<<< HEAD
	pip3 -q install pip --upgrade  && \
    pip3 --no-cache-dir install 	\
	setuptools 						\
    jupyterlab 						\
    && rm -rf /var/lib/apt/lists/*

FROM jupyter-base AS torch

#RUN pip3 --no-cache-dir install torch==1.10.2+cu113 torchvision==0.11.3+cu113 torchaudio==0.10.2+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html

RUN pip3 --no-cache-dir install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu117


#RUN python3.9 -m pip install 'git+https://github.com/facebookresearch/detectron2.git'



FROM torch AS jupytorch
RUN pip3 --no-cache-dir install 	\
	colour							\
	geopandas						\
	labelme2coco				\
	matplotlib					\
	numpy 							\
	opencv-python				\
	opencv-contrib-python			\
	pandas							\
	psutil							\
	rasterio						\
	scikit-image				\
	scikit-learn				\
	scipy 							\
	tqdm

FROM jupytorch AS detectron2

RUN python3.10 -m pip --no-cache-dir install 'git+https://github.com/facebookresearch/detectron2.git' \
                                            'git+https://github.com/facebookresearch/detectron2.git' \                                            
                                              && rm -rf /var/lib/apt/lists/*

FROM detectron2 AS deeplandforms
=======
	pip3 -q install pip --upgrade  \	
	&& rm -rf /var/lib/apt/lists/*



COPY ./requirements.txt /
WORKDIR /
RUN pip3 --no-cache-dir install -r requirements.txt
>>>>>>> 42e5c4e (Major rework, added new notebooks (YOLOv8))

ARG LABPORT=8688
ARG UNAME=user
ARG UID=1000
ARG GID=100
ENV PASSWORD=123456

RUN groupadd -g $GID -o $UNAME && \
        useradd -m -d /home/$UNAME -u $UID -g $GID -s /bin/bash $UNAME && \
        echo "$UNAME:$PASSWORD" | chpasswd
 WORKDIR /home/$UNAME

USER $UNAME
RUN echo "$UNAME"
#EXPOSE 8688
#ENTRYPOINT ["jupyter","lab", "--port=${PORT}","--no-browser", "--ip=0.0.0.0"]
