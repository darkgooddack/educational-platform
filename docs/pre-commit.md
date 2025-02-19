repos:
  - repo: local
    hooks:
      - id: lint
        name: lint
        entry: uv run format
        language: system
        pass_filenames: false

      - id: test
        name: test
        entry: uv run test
        language: system
        pass_filenames: false