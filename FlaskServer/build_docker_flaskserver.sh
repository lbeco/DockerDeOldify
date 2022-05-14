#!/bin/bash

docker build --target builder --tag choonkiatlee/colourize:builder .
docker build --target pip_install --tag choonkiatlee/colourize:pip_install .
docker build --target prepare_release --tag choonkiatlee/colourize:prepare_release .
docker build --target release --tag choonkiatlee/colourize:release .