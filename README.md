# API & Security Automation Platform

FastAPI backend with JWT auth, task CRUD, a small web frontend, a pytest regression suite
(API + security tests), Docker containerization, and GitHub Actions CI/CD.

## Run locally (no Docker)
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements-dev.txt
    pytest -v
    uvicorn app.main:app --reload

## With Docker
    docker compose up --build
    docker compose --profile test run --rm --build tests

## CI/CD
GitHub Actions runs the regression suite and security scans (Bandit, pip-audit, Trivy)
on every pull request, and publishes the image to GHCR on merge to main.
