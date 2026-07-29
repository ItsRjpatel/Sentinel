# Sentinel

Sentinel is a modular feature-first web application.

## First-Time Installation & Bootstrap
Sentinel requires initial setup to establish roles, permissions, and the super administrator.

1. Ensure your database is running and environment variables are set:
```bash
export BOOTSTRAP_ADMIN_PASSWORD="YourSecurePassword123!"
export JWT_SECRET_KEY="YourSecureJWTKey"
```

2. Run the bootstrap script:
```bash
python backend/scripts/bootstrap.py
```
This script is idempotent and can be safely run multiple times without duplicating data.

3. Verify the installation:
```bash
python backend/scripts/check_installation.py
```
It will output a clear `PASS` or `FAIL` for all required infrastructure components.

## Running the Application
To start the application locally:
```bash
cd backend
uvicorn app.main:app --reload
```
