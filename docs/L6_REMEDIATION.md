# L6 remediation plan: validation and staged deployment

Tracks #84.

## Test baseline

- [ ] Add unit tests for deterministic inference and input validation.
- [ ] Add API health/readiness and error-path coverage.
- [ ] Run the project checks in CI and retain the workflow link for the target commit.

## Staged validation

- [ ] Use separate non-production configuration, credentials, and data.
- [ ] Record deploy, smoke-test, monitoring, and rollback results.
- [ ] Document the observable signals (health, errors, latency, and prediction/data quality where applicable).
- [ ] Do not claim a production service until the above evidence is linked from the README or release notes.
