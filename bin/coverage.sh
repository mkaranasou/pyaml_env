#!/bin/bash -e
ROOT_DIR=${PWD}
pytest -s -v --rootdir $ROOT_DIR --cov="${ROOT_DIR}" --cov-report=xml
coverage xml
coverage html -d coverage_html
coverage report --fail-under "80" --skip-covered