# Base Stage
FROM python:3.13.3-slim AS base
WORKDIR /app

# Builder Stage
FROM base AS builder

ARG SONAR_SCANNER_VERSION=6.2.1.4610
ARG OC_CLI_VERSION=stable-4.17
# aarch64, x64
ARG ARCH=aarch64

ENV SONAR_ZIP="sonar-scanner-cli-${SONAR_SCANNER_VERSION}-linux-${ARCH}.zip"

COPY pyproject.toml uv.lock README.md .

RUN --mount=from=ghcr.io/astral-sh/uv,source=/uv,target=/bin/uv \
    uv sync

WORKDIR /opt

## Sonar CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl unzip && \
    curl -fSL "https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/${SONAR_ZIP}" -o sonar-scanner.zip && \
    unzip -qq sonar-scanner.zip && \
    mv "sonar-scanner-${SONAR_SCANNER_VERSION}-linux-${ARCH}" /sonar-scanner && \
    rm sonar-scanner.zip

## Jacoco to Cobertura
RUN curl -fSL "https://gitlab.com/haynes/jacoco2cobertura/-/raw/main/cover2cover.py?ref_type=heads" \
    -o jacoco2cobertura.py && \
    chmod +x jacoco2cobertura.py && \
    mkdir -p /jacoco2cobertura && \
    mv jacoco2cobertura.py /jacoco2cobertura/jacoco2cobertura.py

## Grype
RUN mkdir "/grype" && \
    curl -sSfL "https://raw.githubusercontent.com/anchore/grype/main/install.sh" | sh -s -- -b /grype

# Production Stage
FROM base AS production

LABEL author="Emilio Flores" \
      maintainer="Emilio Flores" \
      description="Pipeline Docker Image"

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /sonar-scanner /tools/sonar-scanner
COPY --from=builder /jacoco2cobertura /tools/jacoco2cobertura
COPY --from=builder /grype /tools/grype

# Install tools
RUN apt-get update && apt-get install -y \
    default-jre-headless \
    openjdk-17-jdk \
    maven \
    docker.io \
    libc6 \
    libstdc++6 \
    libaio1 \
    libaio-dev \
    procps \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Copy Pipeline Code
COPY pipeline pipeline
# Copy resources
COPY resources resources

ENV PATH="/app/.venv/bin:/tools/grype:/tools/sonar-scanner/bin:${PATH}"