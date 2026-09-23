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
KEYWORD_URL = "https://api.digikey.com/products/v4/search/keyword"


class DigiKey:
    """Minimal client covering the part lookup the BOM needs."""

    def __init__(
        self,
        currency: str = "EUR",
        site: str = "DE",
        language: str = "de",
        offline: bool = False,
        refresh: bool = False,
    ):
        # Offline runs answer from the cache only and never need credentials.
        self.offline = offline or not CONFIG_PATH.exists()
        self._config = {} if self.offline else json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self._token = ""
        self._expires_at = 0.0
        self._currency = currency
        self._site = site
        self._language = language
        self.cache = (
            json.loads(CACHE_PATH.read_text(encoding="utf-8"))
            if CACHE_PATH.exists() and not refresh
            else {}
        )

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
        if self.offline:
            return None  # never guess
        url =DETAILS_URL.format(part=urllib.parse.quote(manufacturer_part, safe=""))
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

    def keyword(self, term: str, limit: int = 20) -> list:
        """Keyword search; needed for generic type designations such as 'SS34'.

        The details endpoint only resolves an exact, manufacturer-bound number
        and answers 404 for a type that several makers produce.
        """
        key = f"dkkw:{term}"
        if key in self.cache:
            return self.cache[key] or []
        if self.offline:
            return []
        request =urllib.request.Request(
            KEYWORD_URL,
            data=json.dumps({"Keywords": term, "Limit": limit, "Offset": 0}).encode(),
            headers={**self._headers(), "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.load(response) or {}
        products = (body.get("ExactMatches") or []) + (body.get("Products") or [])
        self.cache[key] = products
        time.sleep(0.6)
        return products

    def save_cache(self) -> None:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(
            json.dumps(self.cache, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def _stock(variation: dict) -> int:
    return int(variation.get("QuantityAvailableforPackageType") or 0)


def _moq(variation: dict) -> int:
    return int(variation.get("MinimumOrderQuantity") or 10**9)


def offer(product: dict | None, quantity: int, how: str = "") -> dict | None:
    """Reduce a product record to the offer for `quantity` pieces.

    Only packagings whose minimum order fits the quantity count: a reel with
    MOQ 3000 is not a prototype buy. Among those, stocked beats unstocked and
    cut tape beats Digi-Reel, whose reeling fee skews a small order.
    """
    if not product:
        return None
    quantity = max(quantity, 1)
    variations = [
        v for v in product.get("ProductVariations") or []
        if _moq(v) <= quantity and v.get("StandardPricing")
    ]
    variations.sort(key=lambda v: (_stock(v) == 0, float(v.get("DigiReelFee") or 0) > 0, _moq(v)))
    result = {
        "part": "",
        "price": None,
        "price_break": None,
        "stock": 0,
        "url": product.get("ProductUrl", ""),
        "lifecycle": (product.get("ProductStatus") or {}).get("Status", ""),
        "end_of_life": bool(product.get("EndOfLife") or product.get("Discontinued")),
        "manufacturer": (product.get("Manufacturer") or {}).get("Name", ""),
        "manufacturer_part": product.get("ManufacturerProductNumber", ""),
        "datasheet": product.get("DatasheetUrl", ""),
        "how": how,
    }
    if not variations:
        # Listed, but only in packagings too large for this order.
        packagings = product.get("ProductVariations") or []
        result["part"] = packagings[0].get("DigiKeyProductNumber", "") if packagings else ""
        return result
    chosen = variations[0]
    breaks = sorted(
        (int(b["BreakQuantity"]), float(b["UnitPrice"]))
        for b in chosen["StandardPricing"]
        if b.get("UnitPrice") is not None
    )
    applicable = [b for b in breaks if b[0] <= quantity] or breaks[:1]
    result.update(
        part=chosen.get("DigiKeyProductNumber", ""),
        price=applicable[-1][1] if applicable else None,
        price_break=applicable[-1][0] if applicable else None,
        stock=_stock(chosen),
    )
    return result
