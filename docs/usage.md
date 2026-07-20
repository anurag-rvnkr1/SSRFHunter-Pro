# 🚀 Usage Guide

This guide covers the basic workflow for using **SSRFHunter Pro** to perform **authorized SSRF security assessments**.

> **⚠️ Disclaimer:** Only scan systems that you own or have explicit permission to assess.

---

## 🔍 Run a Scan

Start an SSRF assessment against a target.

```bash
ssrfhunter scan \
  --url https://example.test \
  --workers 4 \
  --timeout 12 \
  --html \
  --json
```

---

## 🕸️ Crawl a Target

Discover URLs, forms, and endpoints before scanning.

```bash
ssrfhunter crawl \
  --url https://example.test \
  --max-depth 3
```

---

## 📊 Generate Reports

View or regenerate reports for a completed scan.

```bash
ssrfhunter report \
  --scan-id 1 \
  --html
```

---

## 📜 Scan History

Display previously executed scans.

```bash
ssrfhunter history --limit 10
```

---

## 💡 Helpful Commands

```bash
# Show available commands
ssrfhunter --help

# Display version
ssrfhunter version

# Validate installation
ssrfhunter doctor
```

---

## 📂 Output

Generated reports are stored in the configured output directory and are available in:

- 📄 HTML
- 📑 JSON
- 📝 Markdown

These reports include scan details, findings, severity ratings, evidence, and remediation recommendations.

---

### 🛡️ Responsible Usage

SSRFHunter Pro is designed exclusively for **authorized security testing, security research, and educational purposes.** Users are responsible for complying with all applicable laws, regulations, and organizational policies.
