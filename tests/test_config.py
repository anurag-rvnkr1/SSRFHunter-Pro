from ssrfhunter.config.settings import ScanConfig


def test_scan_config_defaults() -> None:
    config = ScanConfig()
    assert config.workers == 4
    assert config.timeout == 10
    assert config.domain_restriction is True


def test_scan_config_merge() -> None:
    config = ScanConfig(target="https://example.com")
    merged = config.merge({"timeout": 20, "verbose": True})
    assert merged.timeout == 20
    assert merged.verbose is True
    assert merged.target == "https://example.com"
