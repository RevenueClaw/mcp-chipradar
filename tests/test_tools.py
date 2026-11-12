"""Tests for MCP tool schemas and demo mode."""

import json
import os
import pytest

from mcp_chipradar.client import ChipRadarClient
import mcp_chipradar.tools as tools


@pytest.mark.asyncio
async def test_keyless_demo_best_provider():
    os.environ.pop("CHIPRADAR_API_KEY", None)
    client = ChipRadarClient()
    assert client.demo_mode is True
    data = await client.get_best_inference_provider("llama-3-8b", "latency")
    assert data["demo_mode"] is True
    assert "instructions" in data
    assert len(data["static_provider_list"]) > 0


@pytest.mark.asyncio
async def test_keyless_demo_breakeven():
    os.environ.pop("CHIPRADAR_API_KEY", None)
    client = ChipRadarClient()
    data = await client.calculate_cloud_vs_local_breakeven(1_000_000, "llama-3-8b")
    assert data["demo_mode"] is True
    assert "instructions" in data
    assert len(data["static_sample_boards"]) > 0


@pytest.mark.asyncio
async def test_tool_outputs_valid_json():
    os.environ.pop("CHIPRADAR_API_KEY", None)
    out = await tools.get_best_inference_provider("llama-3-8b", "balanced")
    json.loads(out)  # must parse
    out = await tools.calculate_cloud_vs_local_breakeven(1_000_000, "llama-3-8b")
    json.loads(out)  # must parse
