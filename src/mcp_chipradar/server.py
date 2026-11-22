"""MCP server for ChipRadar's full-stack AI compute intelligence:
hardware pricing + live cloud-vs-local telemetry (OpenRouter provider scorecards
and break-even math) exposed as MCP tools."""

from mcp.server.fastmcp import FastMCP

from . import tools

mcp = FastMCP(
    "chipradar",
    instructions=(
        "ChipRadar spans the full AI compute stack. Agents use it both to pick the "
        "fastest / most reliable OpenRouter cloud provider in real time (live TTFT, "
        "tok/s, uptime scorecards) and to calculate the break-even local hardware "
        "alternative (vendor-verified board pricing, measured on-board LLM throughput, "
        "power, restock signals). One API key unlocks both the REST API and this MCP "
        "server; a keyless demo mode is available."
    ),
)


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
    """Pick the fastest / most reliable OpenRouter cloud provider for a model in
    real time (live TTFT, tok/s, uptime scorecard)."""
    return await tools.get_best_inference_provider(model=model, priority=priority)


@mcp.tool()
async def calculate_cloud_vs_local_breakeven(
    daily_tokens: int, model: str
) -> str:
    """Calculate the break-even local-hardware alternative to cloud inference:
    vendor board pricing + measured throughput + power vs live cloud cost."""
    return await tools.calculate_cloud_vs_local_breakeven(
        daily_tokens=daily_tokens, model=model
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
