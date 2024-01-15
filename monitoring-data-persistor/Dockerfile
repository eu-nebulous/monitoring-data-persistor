# Copyright (c) 2023 Institute of Communication and Computer Systems
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
FROM python:3.11 as source
#RUN pip install --no-cache-dir --upgrade pip

RUN mkdir /src
COPY ./src/ /src/
WORKDIR /src
RUN pip install --no-cache-dir -r requirements.txt && python3 setup.py sdist
#RUN ls ./dist/


FROM ubuntu:noble

ENV TZ=Europe/Athens
ENV VERSION=1.0.0
ENV LOG_FILE=monitoring_data_persistor.log

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --no-install-recommends -y \
libffi8=3.4.4-2 \
build-essential=12.10ubuntu1 \
libssl-dev=3.0.10-1ubuntu3 \
libffi-dev=3.4.4-2 \
python3-dev=3.11.4-5ubuntu1 \
python3=3.11.4-5ubuntu1 \
python3.11-venv=3.11.7-2 \
python3-pip=23.3+dfsg-1 \
&& rm -rf /var/lib/apt/lists/*

COPY --from=source ./src/dist/monitoring-data-persistor-$VERSION.tar.gz /home/
COPY ./ /home/monitoring-data-persistor-$VERSION
WORKDIR /home
RUN python3 -m venv monitoring-data-env && /bin/sh -c ". monitoring-data-env/bin/activate && pip install --no-cache-dir /home/monitoring-data-persistor-$VERSION.tar.gz"
RUN tar -xzvf /home/monitoring-data-persistor-$VERSION.tar.gz &&  /bin/sh -c ". monitoring-data-env/bin/activate && pip install --no-cache-dir -r /home/monitoring-data-persistor-$VERSION/src/requirements.txt"
#RUN bash -x /home/monitoring-data-persistor-$VERSION/src/prepare_project_code.sh
#COPY ./ /home/monitoring-data-persistor
CMD ["/bin/sh","-c",". monitoring-data-env/bin/activate && python3 -u /home/monitoring-data-persistor-$VERSION/src/main/runtime/DataPersistor.py /home/monitoring-data-persistor-$VERSION/src/resources/config.properties 2>&1 > $LOG_FILE "]