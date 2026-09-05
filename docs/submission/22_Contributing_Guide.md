# Contributing Guide
## AgriDecision AI — Open Source Development Guidelines
**Version:** 1.0 | **Date:** July 28, 2026

---

## 1. Welcome

Thank you for contributing to AgriDecision AI! We welcome contributions from developers, agronomists, data scientists, and UI/UX designers to help advance precision agriculture technology for smallholder farming communities.

---

## 2. Code of Conduct

All contributors are expected to uphold a respectful, inclusive environment. Discriminatory language, harassment, or non-constructive criticism will not be tolerated.

---

## 3. How to Contribute

### 3.1 Reporting Bugs
- Use GitHub Issues to report bugs.
- Include: System environment, OS, step-by-step reproduction steps, expected behavior, and actual error logs.

### 3.2 Feature Requests
- Open a GitHub Discussion or Issue titled `[Feature Request]: Summary`.
- Detail the agronomic or technical value, target users, and proposed implementation design.

### 3.3 Submitting Pull Requests (PRs)
1. Fork the repository and create a branch from `develop`:
   `git checkout -b feature/your-feature-name`
2. Follow strict code formatting:
   - **Python:** `ruff check .` and `black .`
   - **TypeScript/React:** `npm run lint` and `npm run format`
   - **Flutter/Dart:** `dart analyze` and `flutter format .`
3. Write or update tests in `testing/` covering your changes.
4. Ensure all unit and integration tests pass:
   `python -m unittest testing/unit/test_services.py`
5. Push to your fork and submit a Pull Request against `develop`.

---

## 4. Coding Conventions

- **Python:** Follow PEP 8 guidelines. Use type hints for all function signatures. Use Pydantic v2 schemas for API data contracts.
- **Microservices:** Keep business logic in `services/`, database queries in `repositories/`, and endpoints in `routers/`.
- **Git Commits:** Use conventional commit messages (`feat: ...`, `fix: ...`, `docs: ...`, `test: ...`, `refactor: ...`).

---

## 5. Security & Vulnerability Reporting

If you discover a security vulnerability, **do NOT open a public GitHub issue**. Please email `security@agridecision.ai` directly. We will acknowledge receipt within 24 hours and issue a patch within 7 days.
