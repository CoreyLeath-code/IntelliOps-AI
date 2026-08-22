# Changelog

All notable changes to IntelliOps-AI are documented in this file.

The project follows Semantic Versioning and uses Git tags in the form `vMAJOR.MINOR.PATCH`.

## [Unreleased]

No unreleased changes are currently documented.

## [1.0.0] - 2026-08-22

### Added

- Multi-language CI for Python and Go.
- Python coverage and JUnit test artifacts.
- Go race detection, vetting, formatting validation, coverage, and build verification.
- Docker Compose validation and application-image builds.
- CodeQL analysis for Python, Go, and JavaScript/TypeScript.
- Gitleaks, Trivy, pip-audit, Dependabot, and CycloneDX SBOM automation.
- Tag-triggered GitHub Release artifacts and GHCR image publishing.
- Reproducible research-style benchmark harness with committed machine-readable evidence.
- L6 engineering audit with explicit production-readiness gaps and next-step priorities.
- README architecture flow, system-design flow, Quickstart, reproducibility protocol, benchmark interpretation, release contract, and Q&A.

### Hardened

- Go gateway request-method and JSON-shape validation.
- 1 MiB request-body limit and finite four-feature contract.
- Context-aware bounded downstream request behavior.
- Stable 502/503 failure mapping and downstream response-contract validation.
- Documentation language separating measured evidence from production or generalization claims.

### Known limitations

- Model training still occurs lazily in the demonstration path.
- Current classification metrics are a training-corpus sanity check, not held-out generalization evidence.
- Current throughput/latency evidence excludes HTTP, gateway, container, network, concurrency, and GPU execution.
- Authenticated ingress, deployment-specific threat modeling, and production model-artifact promotion remain follow-up work.
