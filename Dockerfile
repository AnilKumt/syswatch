# Multi-stage lightweight Dockerfile for syswatch
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy package metadata and source code
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
COPY config/ ./config/

# Install syswatch package
RUN pip install --no-cache-dir .

# Production runtime image
FROM python:3.12-slim AS runner

WORKDIR /app

# Copy installed Python site-packages and entrypoints from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin/syswatch /usr/local/bin/syswatch
COPY --from=builder /app/config /app/config

# Non-root user setup for unprivileged container runs
RUN useradd -m -u 1000 syswatch && \
    chown -R syswatch:syswatch /app

USER syswatch

# Default CLI entrypoint
ENTRYPOINT ["syswatch"]
CMD ["status"]
