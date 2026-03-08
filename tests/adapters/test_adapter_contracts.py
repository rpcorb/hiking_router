from hiking_router.adapters.osm_client import OSMClient


def test_osm_client_has_fetch_trails_contract():
    client = OSMClient()
    assert hasattr(client, "fetch_trails")
