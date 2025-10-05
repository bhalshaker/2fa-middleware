FROM python:3.13-slim

WORKDIR /2fa-middleware

COPY . .

RUN pip install --no-cache-dir -r app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements-test.txt

# Copy the wait script into the image
COPY wait-for-postgres.sh /usr/local/bin/wait-for-postgres.sh

# Make it executable
RUN chmod +x /usr/local/bin/wait-for-postgres.sh

ENV PYTHONPATH=/app