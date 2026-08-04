# PhishGuard — Phishing Website Detection System

A machine learning based system that classifies URLs as **Phishing** or
**Legitimate** using URL-structure features (no need to fetch page content,
so it works instantly and offline).

---

## 1. Problem Statement

Phishing websites impersonate legitimate services (banks, e-mail providers,
e-commerce sites) to steal credentials and financial information. This
project builds a system that analyzes a URL's structure and flags it as
phishing or legitimate in real time, before the user even opens the page.

## 2. Project Architecture

```
User enters URL
      |
      v
feature_extraction.py  --> extracts 22 numeric/binary features
      |
      v
phishing_model.pkl (Random Forest) --> predicts label + confidence
      |
      v
Flask web app (app.py) --> displays verdict on dashboard UI
```

## 3. Features Used (22 total)

| Category            | Examples                                                  |
|----------------------|------------------------------------------------------------|
| URL structure         | url_length, hostname_length, path_length, num_dots, num_hyphens |
| Special characters     | num_at (@), num_equal, num_underscore, num_percent           |
| Security indicators    | has_https, has_ip_address, is_shortened                     |
| Content signals        | has_suspicious_word (login/verify/secure/etc.), prefix_suffix |
| Structural anomalies   | double_slash_redirect, num_subdomains                        |
| Statistical            | hostname_entropy (randomness of the domain name)              |

Full list and extraction logic: `feature_extraction.py`

## 4. Dataset

`generate_dataset.py` builds a labeled dataset of 1500 URLs (750 legitimate,
750 phishing), including a mix of:
- **Easy examples** — obviously suspicious (IP-based URLs, suspicious TLDs
  like `.tk`/`.ml`, shortened links)
- **Hard examples** (35%) — phishing URLs that mimic legitimate structure
  closely (valid-looking `.com` domains, HTTPS present) and legitimate URLs
  with longer/messier paths, so the model can't rely on shortcuts alone

> **For your final submission**, you can swap this with the real
> **UCI Phishing Websites Dataset** (https://archive.ics.uci.edu/dataset/327)
> or live data from **PhishTank** (https://phishtank.org) — the pipeline
> (`train_model.py`) works unchanged, just point it at a CSV with `url,label`
> columns.

## 5. Model Training & Results

Three models were trained and compared (`train_model.py`):

| Model                | Accuracy | Precision | Recall | F1-score |
|-----------------------|----------|-----------|--------|----------|
| Logistic Regression    | 97.3%    | 94.9%     | 100%   | 97.4%    |
| **Random Forest**       | **99.3%**| **99.3%** | **99.3%** | **99.3%** |
| Gradient Boosting       | 99.3%    | 99.3%     | 99.3%  | 99.3%    |

**Random Forest** was selected as the final model (saved to
`model/phishing_model.pkl`).

**Top predictive features** (feature importance):
1. `has_https` — phishing sites more often skip HTTPS
2. `has_suspicious_word` — words like "verify", "login", "secure" in the URL
3. `path_length`, `num_digits`, `url_length` — phishing URLs tend to be
   longer/more complex to obscure their real destination
4. `hostname_entropy` — randomly generated subdomains have higher entropy

## 6. Web Application

`app.py` (Flask) serves a dashboard where a URL can be pasted and scanned.
Response includes: verdict (Phishing/Legitimate), confidence %, and the
full feature breakdown (expandable) — useful for explaining *why* the
model made its decision during your demo.

## 7. How to Run

```bash
pip install -r requirements.txt
python3 generate_dataset.py     # creates data/urls_dataset.csv
python3 train_model.py          # trains model, saves to model/
python3 app.py                  # starts web server
```
Then open **http://localhost:5000** in your browser.

## 8. How to Present This (Demo Script)

1. **Open with the problem**: show a real phishing URL example (e.g.
   `http://paypal-verify-account.tk/login`) and explain why it's dangerous.
2. **Show the architecture diagram** (Section 2 above).
3. **Live demo**: paste 2-3 URLs into the web app —
   - One obvious phishing link → shows red "PHISHING DETECTED"
   - One legitimate site (e.g. `https://github.com`) → shows green "LEGITIMATE"
   - Click "View extracted features" to show *why* the model decided that
4. **Show the results table** (Section 5) — mention precision/recall
   trade-off: in phishing detection, **recall matters most** (missing a
   real phishing site is worse than a false alarm).
5. **Mention feature importance** — explain in plain words: "the model
   learned that missing HTTPS and suspicious keywords are the strongest
   phishing signals, which matches real-world phishing behavior."
6. **Future scope** (good for Q&A): integrate live WHOIS/domain-age
   lookups, browser extension, real-time PhishTank feed integration.

## 9. Project Structure

```
phishing-detector/
├── data/
│   └── urls_dataset.csv
├── model/
│   ├── phishing_model.pkl
│   ├── feature_names.pkl
│   └── results_summary.txt
├── templates/
│   └── index.html
├── feature_extraction.py
├── generate_dataset.py
├── train_model.py
├── app.py
├── requirements.txt
└── README.md
```

## 10. Limitations (be upfront about these if asked)

- Uses only URL-structure features, not live page content or WHOIS domain
  age (those need internet access at prediction time — easy extension).
- Trained on a synthetically generated dataset for offline reproducibility;
  swapping in the real UCI/PhishTank dataset (Section 4) is recommended
  for a stronger final submission and will change the exact numbers above.
