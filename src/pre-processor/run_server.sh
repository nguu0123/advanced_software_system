#!/bin/bash

export PORT=5001

CMD="uvicorn --host 0.0.0.0 --port $PORT preprocessor:app"

for value in "$@"; do
  if [[ "$value" == "--debug" ]]; then
    CMD="fastapi dev --host 0.0.0.0 --port $PORT preprocessor.py"
    break
  fi
done

$CMD
