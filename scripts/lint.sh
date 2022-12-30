#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports sigy/
poetry run ruff .
poetry run black --check sigy/ tests/
poetry run safety check -i 39462 -i 40291
poetry run bandit -r sigy/
