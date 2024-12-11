#!/bin/bash

export PORT=5002

CMD="uvicorn --host 0.0.0.0 --port $PORT inference:app"

for value in "$@"; do
  if [[ "$value" == "--debug" ]]; then
    CMD="fastapi dev --host 0.0.0.0 --port $PORT inference.py"
    break
  fi
done

$CMD
