# 🤝 Contributing to SSRFHunter Pro

First off, thank you for your interest in contributing to **SSRFHunter Pro**! Every contribution—whether it's fixing a bug, improving documentation, enhancing performance, or adding new features—is greatly appreciated.

---

## 🚀 Getting Started

1. **Fork** this repository.
2. **Clone** your fork locally.
3. Create a new feature branch.

```bash
git checkout -b feature/your-feature-name
```

4. Install the project dependencies.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

---

## 🧪 Before Submitting

Please ensure your changes pass all quality checks.

```bash
pytest

ruff check .

black .

mypy ssrfhunter
```

Your Pull Request should:

- ✅ Pass all tests
- ✅ Follow PEP 8 standards
- ✅ Include type hints where applicable
- ✅ Maintain clean, readable code
- ✅ Include documentation updates (if needed)

---

## 📌 Pull Request Guidelines

When opening a Pull Request, please include:

- A clear description of the change
- Motivation for the change
- Related issue number (if applicable)
- Screenshots or examples (when relevant)

Small, focused pull requests are preferred over large unrelated changes.

---

## 🐞 Reporting Issues

Found a bug or have a feature request?

Please open a GitHub Issue and include:

- Environment details
- Steps to reproduce
- Expected behavior
- Actual behavior
- Relevant logs or screenshots

---

## ⚖️ Code of Conduct

By participating in this project, you agree to follow the guidelines outlined in the **CODE_OF_CONDUCT.md**.

Let's build a secure, reliable, and professional open-source project together. 🚀