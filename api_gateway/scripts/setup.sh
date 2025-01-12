#!/bin/bash
uv venv
source .venv/bin/activate
uv sync
uv pip install -e .