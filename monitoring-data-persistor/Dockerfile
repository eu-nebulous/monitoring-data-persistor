# Use python:3.11 as the source stage to build the package
FROM python:3.11 as source

# Create and set the working directory
RUN mkdir /src
COPY ./src/ /src/
WORKDIR /src

# Install dependencies and package the application
RUN pip install --no-cache-dir -r requirements.txt && python3 setup.py sdist

# Start the final stage using Ubuntu as the base image
FROM ubuntu:noble

# Set the environment variables
ENV TZ=Europe/Athens
ENV VERSION=1.0.0
ENV LOG_FILE=/home/monitoring_data_persistor.log

# Set the timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install the required packages
RUN apt-get update && apt-get install --no-install-recommends -y \
    python3 \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Copy the packaged application from the source stage
COPY --from=source /src/dist/monitoring-data-persistor-$VERSION.tar.gz /home/

# Set the working directory
WORKDIR /home

# Create a virtual environment and install the application package
RUN python3 -m venv monitoring-data-env \
    && . monitoring-data-env/bin/activate \
    && pip install --no-cache-dir monitoring-data-persistor-$VERSION.tar.gz

CMD ["/bin/bash", "-c", "source monitoring-data-env/bin/activate && python3 -u /home/monitoring-data-persistor-$VERSION/src/main/runtime/DataPersistor.py /home/monitoring-data-persistor-$VERSION/src/resources/config.properties > $LOG_FILE 2>&1"]
