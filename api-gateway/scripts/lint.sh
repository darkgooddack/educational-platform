#!/bin/bash
black app/
isort app/
flake8 app/
mypy app/
# pytest tests/