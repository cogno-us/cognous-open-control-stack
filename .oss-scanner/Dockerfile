# Public hub and optional synthetic Python profiles only.
# Separate repositories named by component-lock.json are not imported here.
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY . /src
WORKDIR /src
RUN python -m pip install --no-cache-dir -r tools/requirements-federated-governance.txt
RUN sh .oss-scanner/test-offline.sh
CMD ["/bin/bash"]
