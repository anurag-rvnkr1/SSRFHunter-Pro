from pathlib import Path

from ssrfhunter.payloads.loader import PayloadLoader


def test_payload_loader_defaults() -> None:
    loader = PayloadLoader(path=Path("nonexistent.yml"))
    payloads = loader.load()
    assert "basic" in payloads
    assert "localhost" in payloads
    assert payloads["basic"]


def test_payload_loader_custom(tmp_path: Path) -> None:
    config_file = tmp_path / "payloads.yml"
    config_file.write_text(
        "basic:\n  - http://127.0.0.1\ncloud metadata:\n  - http://169.254.169.254/latest/meta-data/\n",
        encoding="utf-8",
    )
    loader = PayloadLoader(path=config_file)
    payloads = loader.load()
    assert payloads["basic"] == ["http://127.0.0.1"]
    assert payloads["cloud metadata"] == ["http://169.254.169.254/latest/meta-data/"]
