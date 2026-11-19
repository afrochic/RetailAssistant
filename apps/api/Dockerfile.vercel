# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS dependencies
WORKDIR /build
RUN python -m venv /opt/venv
COPY requirements.txt .
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim-bookworm AS runtime
ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_ENV=production PORT=8080
WORKDIR /app
COPY --from=dependencies /opt/venv /opt/venv
RUN groupadd --gid 10001 retail && useradd --uid 10001 --gid retail --no-create-home retail
COPY --chown=retail:retail app.py ./
COPY --chown=retail:retail retail_mvp ./retail_mvp
COPY --chown=retail:retail catalogue ./catalogue
USER retail
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD python -c "import os,urllib.request;urllib.request.urlopen('http://127.0.0.1:'+os.environ['PORT']+'/health',timeout=4)"
CMD ["sh", "-c", "exec python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080} --no-access-log"]
