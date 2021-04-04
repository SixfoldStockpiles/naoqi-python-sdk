#!/usr/bin/env bash

set -e
PWD_ORIGINAL=$(pwd)
cd "$(dirname "$0")"

export PYTHONPATH=$(pwd)/lib/pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327/lib/python2.7/site-packages
export QI_SDK_PREFIX=$(pwd)/lib/pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327
export PATH=$(pwd)/lib/pynaoqi-python2.7-2.8.6.23-linux64-20191127_152327/bin:$PATH

cd $PWD_ORIGINAL