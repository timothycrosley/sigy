#!/bin/bash
set -euxo pipefail

poetry run black sigy/ tests/
poetry run ruff . --fix
