#!/bin/bash

export PORT=5000

CMD="uvicorn --host 0.0.0.0 --port $PORT web_server:app"

for value in "$@"; do
  if [[ "$value" == "--debug" ]]; then
    CMD="fastapi dev --host 0.0.0.0 --port $PORT web_server.py"
    break
  fi
done

$CMD
