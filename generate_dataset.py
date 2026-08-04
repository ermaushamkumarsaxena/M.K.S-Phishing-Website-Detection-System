"""
Generates a labeled dataset of URLs (phishing=1, legitimate=0) using
realistic patterns. This lets the project run fully offline while still
producing a meaningfully learnable dataset for the ML model.

For a production/final submission, you can replace this with the real
UCI Phishing Websites Dataset or PhishTank data (see README.md for links).
"""

import random
import csv

random.seed(42)

LEGIT_DOMAINS = [
    "google.com", "github.com", "wikipedia.org", "amazon.com", "microsoft.com",
    "apple.com", "linkedin.com", "netflix.com", "yahoo.com", "reddit.com",
    "nytimes.com", "bbc.com", "spotify.com", "dropbox.com", "adobe.com",
    "salesforce.com", "paypal.com", "flipkart.com", "irctc.co.in", "sbi.co.in",
    "hdfcbank.com", "icicibank.com", "gov.in", "nic.in", "cricbuzz.com"
]

LEGIT_PATHS = [
    "", "/", "/home", "/about", "/products", "/blog/2024/article",
    "/user/profile", "/search?q=example", "/docs/api", "/contact-us",
    "/help/faq", "/login", "/dashboard", "/settings"
]

SUSPICIOUS_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".club", ".info"]

BRAND_KEYWORDS = [
    "paypal", "amazon", "netflix", "apple", "microsoft", "google", "facebook",
    "instagram", "sbi", "hdfc", "icici", "irctc", "whatsapp", "gmail", "outlook"
]

SUSPICIOUS_WORDS = [
    "login", "verify", "secure", "update", "confirm", "account", "signin",
    "banking", "suspended", "urgent", "password-reset", "billing", "support"
]

SHORTENERS = ["bit.ly", "tinyurl.com", "goo.gl", "t.co", "cutt.ly"]


def random_string(n):
    return "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=n))


def make_legit_url():
    domain = random.choice(LEGIT_DOMAINS)
    path = random.choice(LEGIT_PATHS)
    scheme = "https"
    sub = random.choice(["", "www.", "www.", "app."])
    return f"{scheme}://{sub}{domain}{path}"


def make_phishing_url():
    style = random.choice(["typosquat", "ip", "long_subdomain", "shortener", "suspicious_path", "fake_tld"])
    brand = random.choice(BRAND_KEYWORDS)
    word = random.choice(SUSPICIOUS_WORDS)

    if style == "typosquat":
        # e.g. paypal-secure-login.tk
        tld = random.choice(SUSPICIOUS_TLDS)
        return f"http://{brand}-{word}-{random_string(4)}{tld}/{word}"

    elif style == "ip":
        ip = ".".join(str(random.randint(1, 255)) for _ in range(4))
        return f"http://{ip}/{brand}/{word}.php"

    elif style == "long_subdomain":
        # e.g. secure.login.verify.paypal.com.account-check.tk
        tld = random.choice(SUSPICIOUS_TLDS)
        return f"http://secure.{word}.{brand}.com.{random_string(6)}{tld}/{word}"

    elif style == "shortener":
        shortener = random.choice(SHORTENERS)
        return f"http://{shortener}/{random_string(7)}"

    elif style == "suspicious_path":
        tld = random.choice(SUSPICIOUS_TLDS)
        return f"http://{brand}{random_string(3)}{tld}/{word}/{word}-{random_string(5)}.html"

    else:  # fake_tld
        tld = random.choice(SUSPICIOUS_TLDS)
        return f"http://{brand}{tld}/{word}"


def make_hard_legit_url():
    """Legitimate URLs that look a bit suspicious (long paths, hyphens,
    query params) so the model can't rely on trivial shortcuts."""
    domain = random.choice(LEGIT_DOMAINS)
    path_style = random.choice(["query", "long", "hyphenated", "nested"])
    if path_style == "query":
        path = f"/search?q={random_string(6)}&ref={random_string(4)}"
    elif path_style == "long":
        path = f"/articles/{random_string(8)}/{random_string(10)}"
    elif path_style == "hyphenated":
        path = "/help-center/reset-password-instructions"
    else:
        path = "/account/settings/security/login-history"
    return f"https://www.{domain}{path}"


def make_hard_phishing_url():
    """Phishing URLs that mimic legitimate structure closely (https,
    normal-looking TLD) so the model must rely on subtler signals."""
    brand = random.choice(BRAND_KEYWORDS)
    tld = random.choice([".com", ".net", ".co"])
    variant = random.choice([
        f"https://{brand}-support{tld}/account/verify",
        f"https://accounts-{brand}{tld}/signin",
        f"https://{brand}.{random_string(5)}{tld}/login",
        f"https://www.{brand}{random_string(2)}{tld}/secure/update",
    ])
    return variant


def generate_dataset(n_per_class=500, hard_fraction=0.35):
    rows = []
    n_hard = int(n_per_class * hard_fraction)
    n_easy = n_per_class - n_hard

    for _ in range(n_easy):
        rows.append((make_legit_url(), 0))
    for _ in range(n_hard):
        rows.append((make_hard_legit_url(), 0))

    for _ in range(n_easy):
        rows.append((make_phishing_url(), 1))
    for _ in range(n_hard):
        rows.append((make_hard_phishing_url(), 1))

    random.shuffle(rows)
    return rows


if __name__ == "__main__":
    data = generate_dataset(n_per_class=750)
    with open("data/urls_dataset.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "label"])
        writer.writerows(data)
    print(f"Dataset saved: {len(data)} rows -> data/urls_dataset.csv")
    print("Sample rows:")
    for row in data[:5]:
        print(row)
