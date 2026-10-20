FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PAYMENT_API_URL=http://payment-api:8000 \
    REMEDIATION_WEBHOOK_URL=http://remediation-engine:8001/api/v1/remediation/alert \
    CHECK_INTERVAL_SEC=3.0

WORKDIR /app

# Sécurité : utilisateur non-root
RUN groupadd -g 10003 aiopsgroup && \
    useradd -u 10003 -g aiopsgroup -s /bin/sh -m aiopsuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R aiopsuser:aiopsgroup /app

USER aiopsuser

CMD ["python", "detector.py"]
