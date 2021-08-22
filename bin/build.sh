#!/bin/bash -e
rm -rf venv
python3 -m pip -q install --upgrade pip
python3 -m pip -q install virtualenv
python3 -m virtualenv -q venv/${PWD##*/} 
. venv/${PWD##*/}/bin/activate
pip -q install --upgrade pip
pip -q install -r build_requirements.txt