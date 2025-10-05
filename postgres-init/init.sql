-- CREATE fastapi_user and GRANT Priviledges
CREATE USER fastapi_user WITH ENCRYPTED PASSWORD 'fastapi_pass';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
-- Create User Profile Table
CREATE TABLE IF NOT EXISTS user_profile (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    mobile_number VARCHAR(255),
    is_mobile_number_verified BOOLEAN,
    email_address VARCHAR(255),
    is_email_address_verified BOOLEAN,
    totp_secret_encrypted TEXT,
    is_totp_verified BOOLEAN,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc'),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() AT TIME ZONE 'utc')
);
-- Grant privileges on the new table to the user
GRANT ALL PRIVILEGES ON TABLE user_profile TO fastapi_user;