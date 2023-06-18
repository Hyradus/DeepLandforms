FROM python:3.9.5-slim-buster
# Install tensorboard
RUN pip3 install tensorboard

WORKDIR /mnt/logdir
EXPOSE 8686
ENTRYPOINT ["tensorboard", "--logdir=/logdir/", "--host=0.0.0.0", "--port=8686"]
