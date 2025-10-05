FROM python:3.13-slim

WORKDIR /2fa-middleware

COPY . .

# Copy the wait script into the image
COPY wait-for-postgres-keycloak.sh /usr/local/bin/wait-for-postgres-keycloak.sh

# Make it executable
RUN chmod +x /usr/local/bin/wait-for-postgres-keycloak.sh

RUN pip install --no-cache-dir -r app/requirements.txt
RUN pip install --no-cache-dir -r app/requirements-test.txt

ENV PYTHONPATH=/app