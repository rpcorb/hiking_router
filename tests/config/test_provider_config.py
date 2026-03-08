from hiking_router.config.providers import ProviderConfig


def test_provider_config_defaults_to_overpass_and_tnm():
    cfg = ProviderConfig.from_env({})
    assert cfg.osm_provider == "overpass"
    assert cfg.usgs_provider == "tnm"


def test_provider_config_reads_env_overrides():
    cfg = ProviderConfig.from_env(
        {
            "HIKING_ROUTER_OSM_BASE_URL": "https://example.test/overpass",
            "HIKING_ROUTER_USGS_BASE_URL": "https://example.test/tnm",
            "HIKING_ROUTER_TIMEOUT_SECONDS": "7",
            "HIKING_ROUTER_RETRY_COUNT": "5",
        }
    )
    assert cfg.osm_base_url == "https://example.test/overpass"
    assert cfg.usgs_base_url == "https://example.test/tnm"
    assert cfg.timeout_seconds == 7
    assert cfg.retry_count == 5
