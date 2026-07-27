# Contributing to AgriDecision AI

Thank you for your interest in contributing to the AgriDecision AI platform! Please take a moment to review our branching strategy, semantic versioning rules, and code contribution standards.

---

## 🌿 Branching Strategy

We follow a structured Gitflow & Trunk-Based hybrid branching pattern:

1. `master` / `main`: Production-ready code. Direct pushes are restricted. All changes require an approved Pull Request.
2. `feature/*`: Used for developing new features (e.g., `feature/soil-moisture-alert`).
3. `bugfix/*`: Used for resolving bugs (e.g., `bugfix/jwt-expiry-issue`).
4. `release/vX.Y.Z`: Staging releases prior to production deployments.

---

## 🏷️ Semantic Versioning (SemVer)

We strictly enforce **Semantic Versioning 2.0.0** (`vMAJOR.MINOR.PATCH`):

- **MAJOR** (`v1.0.0` -> `v2.0.0`): Incompatible API schema changes or breaking datastore migrations.
- **MINOR** (`v1.0.0` -> `v1.1.0`): Backward-compatible new functionality (e.g., new ML crop recommendation model).
- **PATCH** (`v1.0.1` -> `v1.0.2`): Backward-compatible bug fixes or security patches.

---

## 🚀 Release Strategy

1. **Pull Request Review**: All PRs require at least 1 approval from a designated Code Owner.
2. **Automated Verification**: GitHub Actions automatically runs linter checks, unit tests, and security audits.
3. **Automated Build & Deploy**: Upon merging into `master`, GitHub Actions builds Docker images, pushes them to Amazon ECR, and commits image tags to the Helm repository. ArgoCD automatically synchronizes the new state with the production EKS cluster.

---

## 🧪 Testing Standards

All code contributions must include corresponding tests:
- Backend code: Add unit/integration tests under `testing/unit` or `testing/integration`.
- Frontend code: Maintain TypeScript type safety and UI component accessibility.

Run test verification prior to submitting PR:
```bash
python -m unittest testing/unit/test_services.py testing/contract/test_pact_contracts.py
```
