#!/usr/bin/env python3
"""DigiKey Product Information V4 client.

Two-legged OAuth (client credentials): no user login, no redirect. The token
lives about ten minutes, so it is fetched lazily and refreshed when it ages
out rather than once per run - a full BOM sweep outlives a single token.

Credentials come from secrets/digikey_api.json (git-ignored).
"""

from __future__ import annotations

import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "secrets" / "digikey_api.json"
CACHE_PATH = ROOT / "tmp" / "bom" / "digikey_cache.json"

TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
DETAILS_URL = "https://api.digikey.com/products/v4/search/{part}/productdetails"


class DigiKey:
    """Minimal client covering the part lookup the BOM needs."""

    def __init__(self, currency: str = "EUR", site: str = "DE", language: str = "de"):
        self._config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self._token = ""
        self._expires_at = 0.0
        self._currency = currency
        self._site = site
        self._language = language
        self.cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}

    # -- authentication ----------------------------------------------------

    def _ensure_token(self) -> str:
        # Refresh a minute early; a token that expires mid-request is a 401.
        if self._token and time.time() < self._expires_at - 60:
            return self._token
        payload = urllib.parse.urlencode(
            {
                "client_id": self._config["client_id"],
                "client_secret": self._config["client_secret"],
                "grant_type": "client_credentials",
            }
        ).encode()
        request = urllib.request.Request(
            TOKEN_URL, data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            token = json.load(response)
        self._token = token["access_token"]
        self._expires_at = time.time() + int(token.get("expires_in", 600))
        return self._token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._ensure_token()}",
            "X-DIGIKEY-Client-Id": self._config["client_id"],
            "X-DIGIKEY-Locale-Site": self._site,
            "X-DIGIKEY-Locale-Language": self._language,
            "X-DIGIKEY-Locale-Currency": self._currency,
        }

    # -- lookup ------------------------------------------------------------

    def details(self, manufacturer_part: str) -> dict | None:
        """Return the product record for a manufacturer part number."""
        key = f"dk:{manufacturer_part}"
        if key in self.cache:
            return self.cache[key]
        url = DETAILS_URL.format(part=urllib.parse.quote(manufacturer_part, safe=""))
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=self._headers()), timeout=30
            ) as response:
                product = (json.load(response) or {}).get("Product")
        except urllib.error.HTTPError as error:
            if error.code == 404:
                product = None
            else:
                raise
        self.cache[key] = product
        time.sleep(0.6)  # stay inside 120 requests/minute
        return product

    def save_cache(self) -> None:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(
            json.dumps(self.cache, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def summarise(product: dict | None) -> dict:
    """Flatten the fields the bill of materials cares about."""
    if not product:
        return {"found": False}
    variations = product.get("ProductVariations") or []
    stock = max(
        [int(v.get("QuantityAvailableforPackageType") or 0) for v in variations] or [0]
    )
    # Prefer a cut-tape variation: a reel with MOQ 3000 is not a prototype buy.
    pick = min(
        variations,
        key=lambda v: int(v.get("MinimumOrderQuantity") or 10**9),
        default={},
    )
    return {
        "found": True,
        "digikey_part": pick.get("DigiKeyProductNumber", ""),
        "manufacturer": (product.get("Manufacturer") or {}).get("Name", ""),
        "status": (product.get("ProductStatus") or {}).get("Status", ""),
        "end_of_life": bool(product.get("EndOfLife")),
        "discontinued": bool(product.get("Discontinued")),
        "stock": stock,
        "price": product.get("UnitPrice"),
        "min_order": pick.get("MinimumOrderQuantity"),
        "url": product.get("ProductUrl", ""),
    }
