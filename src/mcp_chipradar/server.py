"""MCP server exposing ChipRadar board tools via stdio."""

from mcp.server.fastmcp import FastMCP

from . import tools

mcp = FastMCP("chipradar")


@mcp.tool()
async def get_boards(
    family: str | None = None,
    brand: str | None = None,
    limit: int = 20,
) -> str:
    """List tracked boards with specs and current best vendor price."""
    return await tools.get_boards(family=family, brand=brand, limit=limit)


@mcp.tool()
async def get_board_history(asin: str, days: int = 30) -> str:
    """Get historical vendor price points for a board (ASIN)."""
    return await tools.get_board_history(asin, days=days)


@mcp.tool()
async def get_deals(min_score: int = 0, limit: int = 20) -> str:
    """Get current deals sorted by deal score."""
    return await tools.get_deals(min_score=min_score, limit=limit)


@mcp.tool()
async def get_restock_alerts(limit: int = 20) -> str:
    """Get aggregated public restock signals."""
    return await tools.get_restock_alerts(limit=limit)


@mcp.tool()
async def get_best_inference_provider(
    model: str, priority: str = "balanced"
) -> str:
    """Recommend the best cloud inference provider for a model."""
    return await tools.get_best_inference_provider(model=model, priority=priority)


@mcp.tool()
async def calculate_cloud_vs_local_breakeven(
    daily_tokens: int, model: str
) -> str:
    """Compare cloud inference cost vs buying and running a local board."""
    return await tools.calculate_cloud_vs_local_breakeven(
        daily_tokens=daily_tokens, model=model
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
