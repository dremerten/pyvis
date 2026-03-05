FROM python:3.14-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY . .

FROM python:3.14-alpine AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PORT=8003 HOST=0.0.0.0 APP_LOCATION=container
WORKDIR /app

RUN apk upgrade --no-cache

COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /app/v5-unity /app/v5-unity
COPY --from=builder /app/Procfile /app/Procfile
COPY --from=builder /app/runtime.txt /app/runtime.txt
COPY --from=builder /app/README.md /app/README.md
COPY --from=builder /app/imp.py /app/imp.py
COPY --from=builder /app/imp.py /app/v5-unity/imp.py

RUN addgroup --system app && adduser --system --ingroup app --home /app app \
    && chown -R app:app /app
USER app

EXPOSE 8003

CMD ["python", "v5-unity/bottle_server.py"]
