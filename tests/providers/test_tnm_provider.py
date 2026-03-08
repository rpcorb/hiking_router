from hiking_router.providers.tnm import pick_first_download_url


def test_pick_first_download_url_returns_none_on_empty_items():
    assert pick_first_download_url({"items": []}) is None
