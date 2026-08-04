"""
Feature Extraction Module for Phishing Website Detection
-----------------------------------------------------------
Extracts lexical, host-based, and structural features from a URL
that are commonly used to distinguish phishing sites from legitimate ones.

No external API calls required for the core lexical features, so this
runs fully offline. A few optional features (domain age, WHOIS) require
internet access and are marked clearly below.
"""

import re
import math
from urllib.parse import urlparse


SHORTENING_SERVICES = [
    "bit.ly", "goo.gl", "tinyurl.com", "t.co", "ow.ly", "is.gd",
    "buff.ly", "shorte.st", "adf.ly", "cutt.ly", "rebrand.ly"
]

SUSPICIOUS_WORDS = [
    "login", "verify", "account", "secure", "update", "banking",
    "confirm", "signin", "password", "suspended", "urgent", "click"
]


def _shannon_entropy(s):
    if not s:
        return 0
    prob = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in prob)


def _has_ip_address(hostname):
    if not hostname:
        return 0
    ipv4 = re.match(r"^(\d{1,3}\.){3}\d{1,3}$", hostname)
    return 1 if ipv4 else 0


def extract_features(url: str) -> dict:
    """
    Extracts a dictionary of numeric/binary features from a raw URL string.
    Feature values follow the convention: 1 = phishing-indicative, 0 = normal
    (except counts/lengths which are raw numbers).
    """
    url = url.strip()
    parsed = urlparse(url if "://" in url else "http://" + url)
    hostname = parsed.hostname or ""
    path = parsed.path or ""
    full = url.lower()

    features = {}

    # --- Lexical / URL structure features ---
    features["url_length"] = len(url)
    features["hostname_length"] = len(hostname)
    features["path_length"] = len(path)
    features["num_dots"] = url.count(".")
    features["num_hyphens"] = url.count("-")
    features["num_at"] = url.count("@")
    features["num_question_marks"] = url.count("?")
    features["num_equal"] = url.count("=")
    features["num_underscore"] = url.count("_")
    features["num_tilde"] = url.count("~")
    features["num_percent"] = url.count("%")
    features["num_ampersand"] = url.count("&")
    features["num_digits"] = sum(c.isdigit() for c in url)
    features["num_subdomains"] = max(hostname.count(".") - 1, 0) if hostname else 0

    # --- Security / trust indicators ---
    features["has_https"] = 1 if parsed.scheme == "https" else 0
    features["https_in_path"] = 1 if "https" in (path.lower()) else 0  # HTTPS token misuse
    features["has_ip_address"] = _has_ip_address(hostname)
    features["is_shortened"] = 1 if any(s in hostname for s in SHORTENING_SERVICES) else 0

    # --- Suspicious content signals ---
    features["has_suspicious_word"] = 1 if any(w in full for w in SUSPICIOUS_WORDS) else 0
    features["double_slash_redirect"] = 1 if url.rfind("//") > 7 else 0
    features["prefix_suffix"] = 1 if "-" in hostname else 0

    # --- Statistical feature ---
    features["hostname_entropy"] = round(_shannon_entropy(hostname), 3)

    # --- Simple heuristic risk score (not the ML prediction, just for reference) ---
    return features


FEATURE_NAMES = list(extract_features("http://example.com/test").keys())


if __name__ == "__main__":
    test_urls = [
        "http://secure-login-paypal.com.verify-account.tk/signin",
        "https://www.google.com",
        "http://192.168.1.1/update/account",
        "https://github.com/anthropic",
    ]
    for u in test_urls:
        print(u)
        print(extract_features(u))
        print()
