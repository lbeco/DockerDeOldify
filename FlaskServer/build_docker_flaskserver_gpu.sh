#!/bin/bash
docker build -f Dockerfile.gpu --target base --tag choonkiatlee/colourize:base .
docker build -f Dockerfile.gpu --target builder --tag choonkiatlee/colourize:builder .
docker build -f Dockerfile.gpu --target pip_install --tag choonkiatlee/colourize:pip_install .
docker build -f Dockerfile.gpu --target prepare_release --tag choonkiatlee/colourize:prepare_release .
docker build -f Dockerfile.gpu --target release --tag choonkiatlee/colourize:release .