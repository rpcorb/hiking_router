def pick_first_download_url(payload: dict) -> str | None:
    items = payload.get("items", [])
    if not items:
        return None
    return items[0].get("downloadURL")
