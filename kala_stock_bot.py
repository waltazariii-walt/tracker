#!/usr/bin/env python3
"""
Kala Watch Co stock check: Warli Chronograph - Panda

Runs once: fetches the Shopify product JSON and, if any variant is
available, sends an ntfy.sh push notification linking to add-to-cart.
Designed to be run on a schedule (GitHub Actions). Requires the
NTFY_TOPIC environment variable. No third-party packages needed.
"""

import json
import os
import sys
import time
import urllib.request

STORE = "https://kalawatches.com"
HANDLE = "warli-art-edition-panda"
PRODUCT_URL = f"{STORE}/products/{HANDLE}"
JSON_URL = f"{PRODUCT_URL}.js"

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
HEADERS = {"User-Agent": "Mozilla/5.0 (personal stock watcher)"}


def fetch_product():
    req = urllib.request.Request(JSON_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def notify(title, message, click_url):
    req = urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": title, "Priority": "urgent", "Tags": "watch,tada", "Click": click_url},
        method="POST",
    )
    urllib.request.urlopen(req, timeout=15).read()  # raises on failure


def main():
    if not NTFY_TOPIC:
        sys.exit("NTFY_TOPIC is not set")
    product = fetch_product()  # raises on failure -> run goes red
    in_stock = [v for v in product.get("variants", []) if v.get("available")]
    now = time.strftime("%H:%M:%S")
    if in_stock:
        v = in_stock[0]
        cart_link = f"{STORE}/cart/{v['id']}:1"
        print(f"[{now}] IN STOCK! {v.get('title')} -> {cart_link}")
        notify(
            "Kala Warli Panda is IN STOCK",
            f"{product.get('title')} ({v.get('title')}) is available. Tap to add to cart.",
            cart_link,
        )
    else:
        print(f"[{now}] still sold out")

if __name__ == "__main__":
    main()