#!/usr/bin/env bash

set -euo pipefail

# install python 3.12
apt-get update -y
apt-get install -y software-properties-common
add-apt-repository -y ppa:deadsnakes/ppa
apt-get install -y python3.12 python3.12-distutils

# clean apt cache; this keeps the image small
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# install gapper
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
pip install --upgrade setuptools wheel
pip install -e /autograder/source
python3.12 -m pip cache purge
