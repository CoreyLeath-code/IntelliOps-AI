# Contributing to IntelliOps-AI

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

For the Go API:

```bash
cd services/prediction-api-go
go mod download
go test ./...
```

## Required validation

```bash
ruff check services/ml-model-pytorch --select E9,F63,F7,F82
cd services/ml-model-pytorch && pytest test_model.py --cov=.
cd ../prediction-api-go && gofmt -w . && go vet ./... && go test ./... -race
```

Also validate the deployment manifests:

```bash
docker compose config --quiet
docker compose build ml-model go-api dashboard
```

## Pull-request standard

- Use focused branches and conventional commit messages.
- Explain the problem, design decision, test evidence, operational impact, and rollback considerations.
- Add tests for behavior changes.
- Do not commit credentials, tokens, `.env` files, generated artifacts, or production data.
- Keep APIs backward compatible unless the PR documents a migration path.

## Review criteria

Reviewers should assess correctness, security, observability, failure behavior, model reproducibility, performance, maintainability, deployment impact, and rollback safety.
