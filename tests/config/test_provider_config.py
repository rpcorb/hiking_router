from hiking_router.config.providers import ProviderConfig


def test_provider_config_defaults_to_overpass_and_tnm():
    cfg = ProviderConfig.from_env({})
    assert cfg.osm_provider == "overpass"
    assert cfg.usgs_provider == "tnm"
