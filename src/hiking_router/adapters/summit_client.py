from pathlib import Path

from hiking_router.adapters.summit_aggregator import SummitAggregatorClient


class SummitClient(SummitAggregatorClient):
    def __init__(
        self,
        cache_dir: Path = Path("cache"),
        fetch_summits_fn=None,
    ) -> None:
        provider = fetch_summits_fn or (
            lambda _bbox: {"type": "FeatureCollection", "features": []}
        )
        super().__init__(cache_dir=cache_dir, provider_fns=[provider])
