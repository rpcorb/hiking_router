def generate_top_loops(query: dict) -> list[dict]:
    # Placeholder orchestration. Real integration will call ingest/cache/search/scoring.
    return [
        {
            "name": f"Prototype loop near {query.get('near', 'unknown')}",
            "distance_miles": query.get("miles_min", 0),
            "difficulty": query.get("difficulty", "unknown"),
            "score": 0.5,
        }
    ]
