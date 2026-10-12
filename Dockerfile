# ==========================================
# Stage 1: Dependency Builder
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

# Install dependencies + gunicorn into local user prefix
RUN pip install --no-cache-dir --user -r requirements.txt gunicorn


# ==========================================
# Stage 2: Minimal Production Runtime
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/appuser/.local/bin:$PATH \
    PORT=5000

# Security: Create non-root system user
RUN useradd -u 1000 -m appuser

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy application files
COPY app.py .
COPY templates/ ./templates/

# Fix folder ownership for the non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# WSGI production server execution
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]