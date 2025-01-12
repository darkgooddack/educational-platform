@echo off
uv venv
call .venv\Scripts\activate.ps1
uv sync
uv pip install -e .