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
    """List tracked boards with specs, current best vendor price, board economics
    (memory_bandwidth_gbps, derived_bandwidth_gbps, max_q4_model_b, lifecycle_status,
    eol_date, os_support, spec_source_url — NULL until cited), expansion + power
    (m2_nvme_slots, has_oculink, has_usb4_thunderbolt, poe_hat_compatible, idle_watts,
    load_watts, power_source_url — cited measured-wall values only), landed cost
    (landed_price_usd, shipping_usd_us, psu_included, estimated_delivery_days) and
    price analytics (price_90d_low_usd, price_90d_median_usd, price_percentile_90d
    0=at 90d low / 100=at 90d high, stock_stability_30d 0-100%) and the Used/Secondary
    Market floor from eBay (used_floor_usd, used_landed_floor_usd — shipping included
    only when stated, used_condition, used_active_count, used_listing_url with EPN
    tracking, new_vs_used_savings_pct) — Indie tier and above for used fields."""
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
    """Get current deals sorted by deal score, with landed-cost metadata,
    measured-wall power/expansion fields and 90d buy/wait analytics
    (price_percentile_90d: 0 = currently at the 90-day low, 100 = at the high;
    stock_stability_30d: % of valued stock checks with any vendor in stock), plus
    the eBay Used/Secondary Market floor (used_floor_usd, used_landed_floor_usd,
    used_active_count, used_listing_url, new_vs_used_savings_pct) on Indie+ tiers.
    Used prices NEVER alter the new-retail best_price/percentile fields — separate
    layer. Unverified values are NULL, never estimated."""
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
    """Pick the fastest / most reliable OpenRouter cloud provider for a model in
    real time, from live TTFT / tok/s / uptime scorecards.

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
    """Break-even local-hardware alternative to cloud inference: vendor-verified
    board pricing + measured on-board throughput + power vs live cloud cost.

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
