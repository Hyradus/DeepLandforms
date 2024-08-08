FROM nvidia/cuda:12.5.1-runtime-ubuntu24.04
LABEL org.opencontainers.image.authors="Giacomo Nodjoumi <giacomo.nodjoumi@hyranet.info>"

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and its tools
RUN apt update && apt install --no-install-recommends -y \
    git \
    build-essential \
    curl \
    libgl1-mesa-dev \
    libglib2.0-0 \
    python3 \
    python3-dev \
    python3-venv \
    python3-setuptools && \
    rm -rf /var/lib/apt/lists/*

# Create a virtual environment and install pip
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip

# Copy the requirements file and install dependencies in the virtual environment
COPY ./requirements.txt /
RUN /opt/venv/bin/pip install --no-cache-dir -r /requirements.txt

# Install JupyterLab and IPython kernel in the virtual environment
RUN /opt/venv/bin/pip install jupyterlab ipykernel && \
    /opt/venv/bin/python -m ipykernel install --name=venv --user

ARG UNAME
ARG UID
ARG GID
ARG PASSWORD
ARG LABPORT

ENV UNAME=${UNAME}
ENV UID=${UID}
ENV GID=${GID}
ENV PASSWORD=${PASSWORD}
ENV LABPORT=${LABPORT}

# Check if UID already exists and create user if it doesn't
RUN if ! id -u $UNAME >/dev/null 2>&1; then \
        groupadd -g $GID $UNAME && \
        useradd -m -d /home/$UNAME -u $UID -g $GID -s /bin/bash $UNAME && \
        echo "$UNAME:$PASSWORD" | chpasswd; \
    fi

WORKDIR /home/$UNAME

USER $UNAME
ENV PATH="/opt/venv/bin:$PATH"

RUN echo "Running as user: $(whoami)"

EXPOSE 8688
ENTRYPOINT ["bash", "-c", "jupyter lab --ip=0.0.0.0 --no-browser --allow-root --port=${LABPORT} & tensorboard --logdir=/home/${UNAME}/data/logs --port=6006 --host=0.0.0.0"]
