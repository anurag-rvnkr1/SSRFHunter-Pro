<div align="center">

# 🛡️ SSRF-Hunter Pro

### Enterprise-Grade SSRF Security Assessment Framework

*A fast, modular, asynchronous framework for **authorized SSRF security assessments**, built for security researchers, penetration testers, and application security engineers.*

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AsyncIO](https://img.shields.io/badge/AsyncIO-Enabled-5A5A5A?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</div>

---

## 🚀 Overview

**SSRFHunter Pro** is a high-performance **Python-based SSRF Security Assessment Framework** designed for **authorized security testing**, application security reviews, and cybersecurity research.

Built with an asynchronous architecture, it combines intelligent crawling, configurable payload management, response analysis, and professional reporting into a single, extensible framework.

---

## ✨ Key Features

- ⚡ High-performance asynchronous scanning engine
- 🕸️ Intelligent website & API crawler
- 🔍 URL parameter & HTML form discovery
- 📄 OpenAPI / Swagger support
- 📦 YAML-based payload management
- 🧠 Automated response analysis & risk classification
- 📊 Professional HTML, JSON & Markdown reports
- 🗄️ SQLite scan history
- 🎨 Rich interactive CLI
- 🐳 Docker support
- ✅ CI/CD ready architecture

---

## 🏗️ Architecture

```text
CLI
 │
 ▼
Configuration
 │
 ▼
Crawler ───► Scanner Engine
 │              │
 ▼              ▼
Parser      Response Analysis
 │              │
 └──────────────┤
                ▼
        Report Generator
                │
                ▼
          SQLite Database
```

---

## ⚙️ Installation

```bash
git clone https://github.com/anurag-rvnkr1/SSRFHunter-Pro.git

cd SSRFHunter-Pro

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

---

## 🚀 Quick Start

```bash
ssrfhunter scan \
  --url https://example.test \
  --workers 10 \
  --timeout 15 \
  --html \
  --json
```

---

## 📁 Project Structure

```text
ssrfhunter/
├── cli/
├── scanner/
├── crawler/
├── detection/
├── reporting/
├── database/
├── payloads/
├── core/
└── utils/
```

---

## 🧪 Development

```bash
pytest

ruff check .

black .

mypy ssrfhunter
```

---

## 🐳 Docker

```bash
docker compose up --build
```

---

## 📜 Disclaimer

> **SSRFHunter Pro is intended solely for systems you own or have explicit authorization to assess. Users are responsible for ensuring compliance with applicable laws, policies, and contractual obligations.**

---

<div align="center">

### ⭐ If you find this project useful, consider giving it a Star!


</div>
