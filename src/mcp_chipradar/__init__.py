"""mcp-chipradar — MCP server for the ChipRadar hardware pricing API."""

from .client import ChipRadarClient
from .tools import get_boards, get_board_history, get_deals, get_restock_alerts

__all__ = [
    "ChipRadarClient",
    "get_boards",
    "get_board_history",
    "get_deals",
    "get_restock_alerts",
]

__version__ = "0.2.0"
