#!/bin/bash
cd /home/kavia/workspace/code-generation/streamflix-platform-186045-186056/streaming_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

