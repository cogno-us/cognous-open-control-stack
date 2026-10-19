# Public hub and optional synthetic Python profiles only.
# Separate repositories named by component-lock.json are not imported here.
# python:3.12-slim-bookworm
FROM python:3.12-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258
RUN apt-get update && apt-get install -y --no-install-recommends git build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY . /src
WORKDIR /src
RUN python -m pip install --no-cache-dir --require-hashes -r tools/requirements-release.lock
RUN sh .oss-scanner/test-offline.sh
CMD ["/bin/bash"]
