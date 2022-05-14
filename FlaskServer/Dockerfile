FROM python:3.6.10-slim-buster as base

FROM base as builder
RUN mkdir /install
WORKDIR /install

RUN apt-get update && apt-get install -y gcc build-essential wget virtualenv

COPY requirements.txt /requirements.txt

FROM builder as pip_install

ENV VIRTUAL_ENV=/opt/venv
RUN virtualenv -p python3 $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

###### Prepare the image for release
FROM base as prepare_release

RUN apt-get update && apt-get install -y wget libglib2.0-0 libsm6 libxext6 libxrender1

RUN update-ca-certificates
RUN apt-get install openssl -y
RUN apt-get install libgl1-mesa-glx -y
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser

COPY --from=pip_install /opt/venv /opt/venv
RUN mkdir /DeOldifyAPI

RUN chown appuser:appuser /opt/venv
RUN chown appuser:appuser /DeOldifyAPI

USER appuser

WORKDIR /DeOldifyAPI

# Download Weights
RUN mkdir models checkpoints

RUN wget https://aliyun-hexo.oss-cn-beijing.aliyuncs.com/file/ColorizeArtistic_gen.pth -O models/ColorizeArtistic_gen.pth
RUN wget https://download.pytorch.org/models/resnet34-333f7ec4.pth -O checkpoints/resnet34-333f7ec4.pth


# Prepare release
FROM prepare_release as release

WORKDIR /DeOldifyAPI

COPY --chown=appuser:appuser . .

# USER appuser

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 5000
EXPOSE 5555
# USER root
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000","--log-level=debug", "-w", "4", "app:app", "--timeout" , "300" ]


