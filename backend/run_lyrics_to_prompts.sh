#!/bin/bash

# Run the lyrics_to_prompts.py example

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ensure the example directory exists
mkdir -p examples

# Run the example script
python examples/lyrics_to_prompts.py

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 