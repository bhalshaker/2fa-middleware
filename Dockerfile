FROM python:3.13-slim

WORKDIR /2fa-middleware

COPY . .

RUN pip install --no-cache-dir -r app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements-test.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]