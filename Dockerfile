FROM python:3.9-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/app/src HF_HOME=/app/artifacts/model_cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src src
COPY web web
COPY artifacts artifacts
RUN useradd --uid 10001 --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=90s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "retailassist.api:app", "--host", "0.0.0.0", "--port", "8000"]
