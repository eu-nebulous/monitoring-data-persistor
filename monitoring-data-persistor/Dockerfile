# First stage: Build the application
FROM python:3.11 as builder

# Set the working directory in the container
WORKDIR /src

# Copy the source code into the container
COPY ./src/ .

# Install dependencies and build the application package
RUN pip install --no-cache-dir -r requirements.txt && \
    python setup.py sdist

# Second stage: Prepare the runtime environment
FROM python:3.11-slim

# Set environment variables
ENV TZ=Europe/Athens \
    VERSION=1.0.0 \
    LOG_FILE=/home/monitoring_data_persistor.log

# Set the timezone
# Install gcc and other necessary build tools for compiling C extensions
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /home

# Copy the built application package and other necessary files from the builder stage
COPY --from=builder /src/dist/monitoring-data-persistor-$VERSION.tar.gz ./
COPY --from=builder /src/resources ./resources
COPY --from=builder /src/requirements.txt .

# Install the application
# Optionally, cleanup to reduce image size
# This step removes the build tools and libraries after they are no longer needed
# Cleanup the tar.gz file
RUN pip install --no-cache-dir monitoring-data-persistor-$VERSION.tar.gz && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc g++ make libffi-dev libssl-dev && \
    rm monitoring-data-persistor-$VERSION.tar.gz

# Define the entry point command
CMD ["/bin/bash", "-c", "source /home/monitoring-data-env/bin/activate && python3 -u /home/main/runtime/DataPersistor.py /home/resources/config.properties > $LOG_FILE 2>&1"]
