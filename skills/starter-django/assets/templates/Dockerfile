###############################################
# Stage 1: Build Tailwind CSS
###############################################
FROM debian:bookworm-slim AS tailwind-build

ARG TAILWIND_VERSION=4.1.3
ARG TARGETARCH

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && ARCH=$(case ${TARGETARCH} in \
         amd64) echo "x64" ;; \
         arm64) echo "arm64" ;; \
         *) echo "x64" ;; \
       esac) \
    && curl -sL -o /usr/local/bin/tailwindcss \
       "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-${ARCH}" \
    && chmod +x /usr/local/bin/tailwindcss

WORKDIR /build

# Copy only files Tailwind needs to scan for class names
COPY static/css/input.css ./static/css/input.css
COPY templates/ ./templates/
COPY apps/ ./apps/

# Build minified production CSS
RUN tailwindcss -i static/css/input.css -o static/css/tailwind.css --minify

###############################################
# Stage 2: Install Python dependencies
###############################################
FROM python:3.12-slim AS python-deps

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

###############################################
# Stage 3: Runtime
###############################################
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

# Copy installed Python packages from python-deps stage
COPY --from=python-deps /install /usr/local

# Copy application code
COPY . .

# Copy built Tailwind CSS from tailwind-build stage
COPY --from=tailwind-build /build/static/css/tailwind.css ./static/css/tailwind.css

# Collect static files (WhiteNoise will serve these)
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-placeholder \
    DATABASE_URL=sqlite:///tmp/build.db \
    python manage.py collectstatic --no-input 2>/dev/null || true

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
