#!/bin/bash

echo "Waiting for Postgres on port 5432..."

while ! echo > /dev/tcp/postgres/5432; do
  sleep 3
done

echo "Postgres is up. Starting app..."
echo "Waiting for keycloak on port 8080..."

while ! echo > /dev/tcp/keycloak/8080; do
  sleep 3
done

echo "keycloak is up. Starting app..."
exec "$@"