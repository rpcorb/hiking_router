from hiking_router.providers.tnm import pick_best_download_url


def test_pick_best_download_url_prefers_higher_resolution_products():
    payload = {
        "items": [
            {"downloadURL": "https://example.test/30m.tif", "title": "DEM 1 arc-second"},
            {"downloadURL": "https://example.test/10m.tif", "title": "DEM 1/3 arc-second"},
        ]
    }

    best = pick_best_download_url(payload)

    assert best == "https://example.test/10m.tif"


def test_pick_best_download_url_skips_items_without_download_url():
    payload = {
        "items": [
            {"title": "broken"},
            {"downloadURL": "https://example.test/good.tif", "title": "DEM 1/3 arc-second"},
        ]
    }

    best = pick_best_download_url(payload)

    assert best == "https://example.test/good.tif"
