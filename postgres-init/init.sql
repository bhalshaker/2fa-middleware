-- FastAPI DB
CREATE DATABASE fastapi_db;
CREATE USER fastapi_user WITH ENCRYPTED PASSWORD 'fastapi_pass';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;

-- Keycloak DB
CREATE DATABASE keycloak_db;
CREATE USER keycloak_user WITH ENCRYPTED PASSWORD 'keycloak_pass';
GRANT ALL PRIVILEGES ON DATABASE keycloak_db TO keycloak_user;