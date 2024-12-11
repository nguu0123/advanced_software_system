FROM debian:stable-slim

WORKDIR /web-server

WORKDIR /inference


RUN apt-get update

RUN apt-get install -y git wget make build-essential

RUN git clone https://github.com/pjreddie/darknet.git

RUN cd darknet

WORKDIR /inference/darknet
RUN make

RUN wget https://pjreddie.com/media/files/yolov3-tiny.weights

COPY --from=ghcr.io/astral-sh/uv:0.4.3 /uv /bin/uv

COPY ./pyproject.toml ./

COPY ./run_server.sh ./run_server.sh

RUN uv python pin 3.10 &&\
  uv sync --compile-bytecode --no-cache

COPY ./*.py ./

EXPOSE 5002

ENV PATH=".venv/bin:$PATH"

ENTRYPOINT [ "./run_server.sh" ]

