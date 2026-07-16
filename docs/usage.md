# Usage Guide

## Running a Scan

Use the CLI to perform authorized SSRF assessments:

```bash
ssrfhunter scan --url https://example.test --workers 4 --timeout 12 --html --json
```

## Crawling

```bash
ssrfhunter crawl --url https://example.test --max-depth 3
```

## Reports

```bash
ssrfhunter report --scan-id 1 --html
```

## History

```bash
ssrfhunter history --limit 10
```
