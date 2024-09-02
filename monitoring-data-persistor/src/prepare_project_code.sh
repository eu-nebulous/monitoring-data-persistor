#!/bin/bash
VERSION="1.0.0"


pip install monitoring-data-persistor-$VERSION.tar.gz
tar -xzvf monitoring-data-persistor-$VERSION.tar.gz

pip3 install -r requirements.txt
