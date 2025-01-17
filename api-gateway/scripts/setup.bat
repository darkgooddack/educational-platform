@echo off
uv venv
.venv\Scripts\activate.ps1
uv sync
uv pip install -e ".[dev]"