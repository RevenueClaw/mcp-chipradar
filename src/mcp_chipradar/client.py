"""Low-level async HTTP client for the ChipRadar B2B API."""

import os
from typing import Any, Dict, List, Optional

import httpx


REGISTRATION_INSTRUCTIONS = (
    "This response is running in DEMO mode because CHIPRADAR_API_KEY is not set. "
    "Register for an instant free API key at chipradar.io/api/keys "
    "(100 requests/mo, 5 requests/min) and set CHIPRADAR_API_KEY. "
    "See chipradar.io/developers for paid tiers."
)


class ChipRadarClient:
    """Thin async client for ChipRadar B2B endpoints."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        public_base: str = "https://chipradar.io",
    ):
        self.api_key = api_key or os.environ.get("CHIPRADAR_API_KEY")
        self.base_url = (base_url or os.environ.get(
            "CHIPRADAR_API_BASE", "https://chipradar.io/api/v1"
        )).rstrip("/")
        self.public_base = public_base.rstrip("/")
        self.timeout = timeout
        self.demo_mode = not bool(self.api_key)

    def _headers(self) -> Dict[str, str]:
        if not self.api_key:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if self.demo_mode:
            raise RuntimeError(
                "Authenticated ChipRadar endpoints require CHIPRADAR_API_KEY. "
                "Register at chipradar.io/api/keys for an instant free key."
            )
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout
        ) as client:
            response = await client.request(
                method,
                path,
                params=params,
                json=json_body,
                headers=self._headers(),
            )
            if response.status_code == 401:
                raise RuntimeError(
                    f"ChipRadar API 401 Unauthorized — check CHIPRADAR_API_KEY. "
                    f"{response.text}"
                )
            if response.status_code == 429:
                raise RuntimeError(
                    f"ChipRadar API 429 Rate limit exceeded. "
                    f"Headers: {dict(response.headers)}"
                )
            response.raise_for_status()
            return response.json()

    async def _fetch_public_demo_products(self) -> list:
        url = f"{self.public_base}/api/products/current"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json() or {}
                products = data.get("products") if isinstance(data, dict) else None
                return products if isinstance(products, list) else []
        except Exception as exc:
            return [{"_demo_fetch_error": str(exc), "source": url}]

    def _demo_payload(self, products: list) -> Dict[str, Any]:
        return {
            "demo_mode": True,
            "instructions": REGISTRATION_INSTRUCTIONS,
            "public_source": f"{self.public_base}/api/products/current",
            "sample_count": min(len(products), 5),
        }

    @staticmethod
    def _to_demo_board(product: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "name": product.get("name"),
            "sku": product.get("sku"),
            "best_price": product.get("best_price"),
            "stock": product.get("stock"),
            "best_seller": product.get("best_seller"),
            "url": product.get("url"),
        }

    async def get_boards(
        self,
        family: Optional[str] = None,
        brand: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        if self.demo_mode:
            products = await self._fetch_public_demo_products()
            payload = self._demo_payload(products)
            filtered = [
                p for p in products
                if not isinstance(p, dict) or not p.get("_demo_fetch_error")
            ]
            payload["sample_public_boards"] = [
                self._to_demo_board(p) for p in filtered[:limit]
            ]
            payload["note"] = (
                "get_boards demo uses the public product feed. "
                "With CHIPRADAR_API_KEY, this tool returns full board specs and vendor prices."
            )
            return payload
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if family:
            params["family"] = family
        if brand:
            params["brand"] = brand
        return await self.request("GET", "/boards", params=params)

    async def get_board_history(self, asin: str, days: int = 30) -> Dict[str, Any]:
        if self.demo_mode:
            products = await self._fetch_public_demo_products()
            payload = self._demo_payload(products)
            payload["note"] = (
                f"get_board_history({asin!r}, days={days}) requires CHIPRADAR_API_KEY. "
                "Demo returns sample public boards only."
            )
            payload["sample_public_boards"] = [
                self._to_demo_board(p) for p in products[:5]
            ]
            return payload
        return await self.request(
            "GET", f"/boards/{asin}/history", params={"days": days}
        )

    async def get_deals(self, min_score: int = 0, limit: int = 20) -> Dict[str, Any]:
        if self.demo_mode:
            products = await self._fetch_public_demo_products()
            payload = self._demo_payload(products)
            payload["note"] = (
                f"get_deals(min_score={min_score}, limit={limit}) requires CHIPRADAR_API_KEY. "
                "Demo returns sample public boards only."
            )
            payload["sample_public_boards"] = [
                self._to_demo_board(p) for p in products[:limit]
            ]
            return payload
        return await self.request(
            "GET", "/deals", params={"min_score": min_score, "limit": limit}
        )

    async def get_restock_alerts(self, limit: int = 20) -> Dict[str, Any]:
        if self.demo_mode:
            products = await self._fetch_public_demo_products()
            payload = self._demo_payload(products)
            payload["note"] = (
                f"get_restock_alerts(limit={limit}) requires CHIPRADAR_API_KEY. "
                "Demo returns sample public boards only."
            )
            payload["sample_public_boards"] = [
                self._to_demo_board(p) for p in products[:limit]
            ]
            return payload
        return await self.request("GET", "/restocks", params={"limit": limit})

    async def get_best_inference_provider(
        self, model: str, priority: str = "balanced"
    ) -> Dict[str, Any]:
        """GET /api/v1/inference/recommend wrapper."""
        if self.demo_mode:
            return self._inference_demo_payload(
                "get_best_inference_provider",
                model=model,
                priority=priority,
                static_providers=[
                    {
                        "provider_slug": "openrouter",
                        "display_name": "OpenRouter",
                        "note": "Live pricing/metrics require a CHIPRADAR_API_KEY.",
                    },
                    {
                        "provider_slug": "together",
                        "display_name": "Together AI",
                        "note": "Live pricing/metrics require a CHIPRADAR_API_KEY.",
                    },
                    {
                        "provider_slug": "fireworks",
                        "display_name": "Fireworks AI",
                        "note": "Live pricing/metrics require a CHIPRADAR_API_KEY.",
                    },
                ],
            )
        return await self.request(
            "GET",
            "/inference/recommend",
            params={"model": model, "priority": priority},
        )

    async def calculate_cloud_vs_local_breakeven(
        self, daily_tokens: int, model: str
    ) -> Dict[str, Any]:
        """GET /api/v1/inference/breakeven wrapper."""
        if self.demo_mode:
            return self._inference_demo_payload(
                "calculate_cloud_vs_local_breakeven",
                daily_tokens=daily_tokens,
                model=model,
                static_boards=[
                    {
                        "asin": "B0CK2FCG1K",
                        "name": "Raspberry Pi 5 8GB",
                        "note": "Sample board; live prices and benchmarks require a CHIPRADAR_API_KEY.",
                    }
                ],
            )
        return await self.request(
            "GET",
            "/inference/breakeven",
            params={"daily_tokens": daily_tokens, "model": model},
        )

    def _inference_demo_payload(
        self,
        tool: str,
        *,
        static_providers: Optional[List[Dict[str, Any]]] = None,
        static_boards: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return {
            "demo_mode": True,
            "tool": tool,
            "instructions": REGISTRATION_INSTRUCTIONS,
            "params": kwargs,
            "static_provider_list": static_providers or [],
            "static_sample_boards": static_boards or [],
            "note": (
                f"{tool} requires a paid CHIPRADAR_API_KEY (Indie/Builder tier or above). "
                "This static demo returns placeholder providers/boards, not live metrics or prices."
            ),
        }
