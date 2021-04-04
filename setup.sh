#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"

mkdir -p $(pwd)/lib
wget https://community-static.aldebaran.com/resources/2.8.6/pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327.tar.gz -P lib
cd lib && tar -xzf pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327.tar.gz; cd ..
