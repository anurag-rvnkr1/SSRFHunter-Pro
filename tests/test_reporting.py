from datetime import datetime, timezone

from ssrfhunter.models.models import ScanResult, ScanSummary
from ssrfhunter.reporting.generator import ReportGenerator


def test_report_generator_html(tmp_path):
    summary = ScanSummary(
        scan_id="test",
        target="https://example.com",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        duration_seconds=1.0,
        findings=[],
        statistics={"urls_tested": 1, "findings": 0, "payload_categories": 1},
    )
    result = ScanResult(summary=summary, findings=[], reports={})
    generator = ReportGenerator(template_dir=tmp_path)
    (tmp_path / "report.html.j2").write_text(
        "<html>{{ result.summary.target }}</html>", encoding="utf-8"
    )
    html = generator.generate_html(result)
    assert "https://example.com" in html


def test_report_generator_json():
    summary = ScanSummary(
        scan_id="test",
        target="https://example.com",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        duration_seconds=1.0,
        findings=[],
        statistics={"urls_tested": 1, "findings": 0, "payload_categories": 1},
    )
    result = ScanResult(summary=summary, findings=[], reports={})
    generator = ReportGenerator()
    payload = generator.generate_json(result)
    assert "scan_id" in payload
