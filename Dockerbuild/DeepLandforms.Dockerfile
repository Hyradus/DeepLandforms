
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

MAINTAINER "Giacomo Nodjoumi <giacomo.nodjoumi@hyranet.info>"

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and its tools
RUN apt update && apt install --no-install-recommends -y 	\
    git 							\
    build-essential 				\
    curl 							\
    libgl1-mesa-dev 				\
    libglib2.0-0 					\    
    python3.10-dev 					\
    python3.10-distutils 			&& \
    rm -rf /var/lib/apt/lists/*	    && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
	python3.10 get-pip.py 									&& \
	pip3 -q install pip --upgrade  \	
	&& rm -rf /var/lib/apt/lists/*



COPY ./requirements.txt /
WORKDIR /
RUN pip3 --no-cache-dir install -r requirements.txt

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
