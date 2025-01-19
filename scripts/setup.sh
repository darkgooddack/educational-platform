#!/bin/bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"