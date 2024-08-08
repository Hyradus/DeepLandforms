ARG BASE_IMAGE=jupyter/base-notebook:python-3.9.7
FROM $BASE_IMAGE

LABEL org.opencontainers.image.authors="Giacomo Nodjoumi <giacomo.nodjoumi@hyranet.info>"

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV TZ=Europe/Rome
ENV DEBIAN_FRONTEND=noninteractive

ARG UNAME
ARG UID
ARG GID

USER root

# Install required packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    apt-transport-https \
    build-essential \
    ca-certificates \
    curl \
    git \
    libgl1-mesa-dev \
    libglib2.0-0 \
    locales \
    python3-tk \
    software-properties-common \
    sudo \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 --no-cache-dir install \
    git+https://${GITHUB_TOKEN}@github.com/Hyradus/maxrect.git \
    rio-cogeo \
    && mamba install -c conda-forge -y \
    fiona \
    joblib \
    geopandas \
    geoplot \
    matplotlib \
    numpy \
    opencv \
    psutil \
    pygeos \
    rasterio \
    scikit-image \
    largestinteriorrectangle \
    scipy \
    shapely \
    spectral \
    tqdm \
    && conda clean -a

# Create user with specified UID and GID
RUN groupadd -g $GID $UNAME && \
    useradd -m -d /home/$UNAME -u $UID -g $GID -s /bin/bash $UNAME && \
    chown -R $UNAME:$GID /home/$UNAME

# Set the working directory and add files
WORKDIR /home/$UNAME/IPU
COPY ./IPU /home/$UNAME/IPU
RUN chown -R $UNAME:$GID /home/$UNAME/IPU

USER $UNAME
WORKDIR /home/$UNAME/
