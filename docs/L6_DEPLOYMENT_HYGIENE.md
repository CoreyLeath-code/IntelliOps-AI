# IntelliOps-AI L6 Nine-Tier Deployment Hygiene

This document defines the repository's engineering maturity baseline and the automated evidence produced for each tier.

## Tier 1 — Source Hygiene

- Python syntax validation.
- High-confidence Ruff correctness checks.
- Go formatting enforcement.
- Reproducible development dependencies.

## Tier 2 — Test Engineering

- Python model unit tests on Python 3.10 and 3.11.
- Coverage XML and JUnit artifacts.
- Go tests with race detection and coverage output.
- Deterministic CI execution on every pull request.

## Tier 3 — Static Quality

- Ruff correctness gates.
- Go vet.
- Go build validation.
- CodeQL analysis for Python, Go, and JavaScript/TypeScript.

## Tier 4 — Security Engineering

- Gitleaks secret scanning.
- Trivy filesystem vulnerability scanning.
- Private vulnerability reporting guidance.
- Security findings uploaded through GitHub code scanning.

## Tier 5 — Supply-Chain Hygiene

- Dependabot for Python, Go modules, npm, GitHub Actions, and Docker.
- pip-audit reports.
- CycloneDX SBOM generation.
- Explicit runtime and development dependency manifests.

## Tier 6 — Reproducible Runtime

- Dockerized model, API, and dashboard services.
- Docker Compose configuration validation.
- Independent image builds for deployable application services.
- Environment-driven service integration.

## Tier 7 — Continuous Delivery

- Pull-request and main-branch verification.
- Concurrency cancellation for superseded runs.
- Multi-language compatibility and build gates.
- Release-readiness metadata contract.

## Tier 8 — Release Engineering

- Semantic version tag trigger.
- GitHub Release source artifacts.
- Generated release notes.
- GHCR publishing for model, API, and dashboard images.

## Tier 9 — Operational Governance

- SECURITY.md disclosure process.
- CONTRIBUTING.md validation and review standard.
- Changelog and semantic-versioning policy.
- Auditable CI artifacts for tests, coverage, dependency findings, and SBOMs.
- Deployment-hygiene documentation aligned with the microservice architecture.

## Promotion Standard

A change is release-ready when Python and Go validation, container builds, security workflows, dependency audits, and the release-readiness contract are green. Advisory findings should be tracked as focused remediation work rather than hidden or ignored.
