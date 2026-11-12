# mcp-chipradar

A Model Context Protocol (MCP) server that turns the [ChipRadar](https://chipradar.io)
hardware-pricing API into LLM tools. Query single-board computers, mini PCs,
vendor prices, deal scores, restock alerts, and LLM-on-board benchmarks directly
from Claude, Cursor, OpenClaw / RockClaw, n8n, or any MCP host.

## Quickstart (no API key needed)

The server runs in **demo mode** without `CHIPRADAR_API_KEY`, returning public
demo data and clear setup instructions so registry reviewers can test it in a
single copy-paste.

```bash
# uv / pipx install from the repo sub-directory
pipx install git+https://github.com/RevenueClaw/chipradar.git#subdirectory=mcp-chipradar

# or clone and install locally
git clone https://github.com/RevenueClaw/chipradar.git
cd chipradar/mcp-chipradar
pip install -e .
```

Then add an MCP config block below. Without an API key, `get_boards` returns
sample public boards from `https://chipradar.io/api/products/current`; other tools
return the same public sample plus a registration note.

## API key setup

Get a free key instantly at [chipradar.io/api/keys](https://chipradar.io/api/keys)
(no approval). Paid tiers unlock higher rate limits and features such as
90-day price history and LLM benchmarks.

| Tier | Price | Monthly cap | Per-minute | Unlocks |
|---|---|---|---|---|
| **Sandbox / Free** | `$0/mo` | 100 | 5 | current deals, basic specs |
| **Indie / Builder** | `$12/mo` | 5,000 | 30 | 90-day history, MCP access, **LLM benchmarks** |
| **Pro / Growth** | `$49/mo` | 50,000 | 120 | full history, restock webhooks |
| **Enterprise / Supply Chain** | `$199/mo` | 250,000+ | 600 | bulk exports, priority webhooks, custom SKUs |

Set these environment variables wherever you run the server:

```bash
export CHIPRADAR_API_KEY="sk_cr_..."   # required for live B2B data
export CHIPRADAR_API_BASE="https://chipradar.io/api/v1"  # optional
```

## MCP config snippets

### OpenClaw / RockClaw (`~/.openclaw/mcp.json` or Control UI)

```json
{
  "mcpServers": {
    "chipradar": {
      "command": "mcp-chipradar",
      "env": {
        "CHIPRADAR_API_KEY": "sk_cr_...",
        "CHIPRADAR_API_BASE": "https://chipradar.io/api/v1"
      }
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "chipradar": {
      "command": "mcp-chipradar",
      "env": {
        "CHIPRADAR_API_KEY": "sk_cr_...",
        "CHIPRADAR_API_BASE": "https://chipradar.io/api/v1"
      }
    }
  }
}
```

### Cursor (Settings → MCP → Add server)

Use **Type: Command** and paste:

```bash
CHIPRADAR_API_KEY=sk_cr_... CHIPRADAR_API_BASE=https://chipradar.io/api/v1 mcp-chipradar
```

Or add to your shell profile and just run `mcp-chipradar`.

### n8n (HTTP Request or MCP node)

Point the n8n MCP node at the stdio command:

```text
Command: mcp-chipradar
Environment Variables:
  CHIPRADAR_API_KEY = sk_cr_...
  CHIPRADAR_API_BASE = https://chipradar.io/api/v1
```

## Tools

- `get_boards(family=None, brand=None, limit=20)` — list tracked boards with specs and the best in-stock vendor price.
- `get_board_history(asin, days=30)` — historical vendor price points for a board.
- `get_deals(min_score=0, limit=20)` — boards priced below MSRP, sorted by deal score.
- `get_restock_alerts(limit=20)` — aggregated public restock signals.
- `get_best_inference_provider(model, priority="balanced")` — recommend the best cloud inference provider for a model by cost, latency, or balanced score. Requires a paid API key; keyless mode returns a demo note + static provider list.
- `calculate_cloud_vs_local_breakeven(daily_tokens, model)` — compare 30-day cloud inference spend vs. buying a local board (cheapest in-stock non-Amazon price + on-device throughput). Requires a paid API key; keyless mode returns demo instructions + a sample board.

> **Note:** `get_board_history` and `get_deals` return free-tier limits unless
the active key is Indie or higher. LLM benchmark data lives at
`GET /api/v1/benchmarks/llm` and requires the **Indie/Builder tier or above**
($12/mo); it is available via the API. The two new inference tools call
`GET /api/v1/inference/recommend` and `GET /api/v1/inference/breakeven`
respectively.

## Example prompts

1. *“Find me the cheapest in-stock 8 GB ARM board right now.”*  
   → `get_boards(brand="Raspberry Pi", limit=10)` or `get_deals(limit=10)`

2. *“Show me the 90-day price history for Raspberry Pi 5 8 GB.”*  
   → `get_board_history(asin="B0CK2FCG1K", days=90)`

3. *“What is the best sub-$500 mini PC for running Qwen 32B by tokens-per-dollar?”*  
   → `get_boards(family="mini_pc", limit=20)`, then use the **Indie+ API**
   `GET /api/v1/benchmarks/llm?platform=mini_pc` to rank by
   `perf_per_dollar` (tokens/sec per dollar) and filter by `usd_price < 500`.

## Running keyless (demo mode)

```bash
CHIPRADAR_API_BASE=https://bad-host.example mcp-chipradar
```

With no `CHIPRADAR_API_KEY`, the server ignores `CHIPRADAR_API_BASE` and serves
public demo data with registration instructions instead of crashing.

## Telemetry / limits

Every live response includes `X-RateLimit-*` headers. The free Sandbox tier is
100 requests/month and 5 requests/minute — plenty for evaluation.

## Changelog

- **0.2.0** — Added inference telemetry tools:
  - `get_best_inference_provider(model, priority)`
  - `calculate_cloud_vs_local_breakeven(daily_tokens, model)`
  - Keyless demo mode now returns a registration note + static provider/sample-board list so the server boots cleanly without `CHIPRADAR_API_KEY`.

## License

Apache-2.0 — see [LICENSE](./LICENSE) in this package.
