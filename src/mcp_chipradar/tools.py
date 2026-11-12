"""Tool implementations used by the MCP server."""

import json
from typing import Any, Dict, Optional

from .client import ChipRadarClient


def _format_error(tool: str, exc: Exception) -> str:
    payload: Dict[str, Any] = {
        "success": False,
        "tool": tool,
        "error": str(exc),
        "help": (
            "Set CHIPRADAR_API_KEY to use live data (get a free key at "
            "chipradar.io/api/keys). Running keyless returns demo data and "
            "registration instructions."
        ),
    }
    return json.dumps(payload, indent=2)


async def _client() -> ChipRadarClient:
    return ChipRadarClient()


async def get_boards(
    family: Optional[str] = None,
    brand: Optional[str] = None,
    limit: int = 20,
) -> str:
    """List tracked boards with specs and current best vendor price."""
    try:
        client = await _client()
        data = await client.get_boards(family=family, brand=brand, limit=limit)
        return json.dumps(data, indent=2)
    except Exception as exc:
        return _format_error("get_boards", exc)


async def get_board_history(asin: str, days: int = 30) -> str:
    """Get historical vendor price points for a board (ASIN)."""
    try:
        client = await _client()
        data = await client.get_board_history(asin, days=days)
        return json.dumps(data, indent=2)
    except Exception as exc:
        return _format_error("get_board_history", exc)


async def get_deals(min_score: int = 0, limit: int = 20) -> str:
    """Get current deals sorted by deal score."""
    try:
        client = await _client()
        data = await client.get_deals(min_score=min_score, limit=limit)
        return json.dumps(data, indent=2)
    except Exception as exc:
        return _format_error("get_deals", exc)


async def get_restock_alerts(limit: int = 20) -> str:
    """Get aggregated public restock signals."""
    try:
        client = await _client()
        data = await client.get_restock_alerts(limit=limit)
        return json.dumps(data, indent=2)
    except Exception as exc:
        return _format_error("get_restock_alerts", exc)


async def get_best_inference_provider(
    model: str, priority: str = "balanced"
) -> str:
    """Recommend the best cloud inference provider for a model.

    Args:
        model: ChipRadar inference model slug, e.g. "llama-3-8b".
        priority: One of "cost", "latency", or "balanced" (default).
    """
    try:
        client = await _client()
        data = await client.get_best_inference_provider(model=model, priority=priority)
        return json.dumps(data, indent=2)
    except Exception as exc:
        return _format_error("get_best_inference_provider", exc)


async def calculate_cloud_vs_local_breakeven(
    daily_tokens: int, model: str
) -> str:
    """Compare cloud inference cost vs buying a local board.

    Args:
        daily_tokens: Expected tokens generated per day.
        model: ChipRadar inference model slug, e.g. "llama-3-8b".
    """
    try:
        client = await _client()
        data = await client.calculate_cloud_vs_local_breakeven(
            daily_tokens=daily_tokens, model=model
        )
        return json.dumps(data, indent=2)
    except Exception as exc:
        return _format_error("calculate_cloud_vs_local_breakeven", exc)
