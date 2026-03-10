# ─────────────────────────────────────────────────────────────
# Stage 1: builder — install deps into a venv
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    libwebp-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtualenv
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt


# ─────────────────────────────────────────────────────────────
# Stage 2: runtime — lean final image
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

LABEL maintainer="placeholder-service"
LABEL description="Placeholder Image Generator API + UI"

# Runtime libs for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    libwebp7 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /service

# Copy application source
COPY app/ ./app/

EXPOSE 8000

# Unprivileged user
RUN useradd -m -u 1000 appuser && chown -R appuser /service
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
