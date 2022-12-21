#!/bin/bash
set -euxo pipefail

poetry run isort sigy/ tests/
poetry run black sigy/ tests/
