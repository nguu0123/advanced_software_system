FROM debian:stable-slim

WORKDIR /preproc-server

COPY --from=ghcr.io/astral-sh/uv:0.4.3 /uv /bin/uv

COPY ./pyproject.toml ./

COPY ./run_server.sh ./run_server.sh

RUN uv python pin 3.10 &&\
  uv sync --compile-bytecode --no-cache

COPY ./*.py ./

COPY ./helpers/ ./helpers/

EXPOSE 5001

ENV PATH=".venv/bin:$PATH"

ENTRYPOINT [ "./run_server.sh" ]

