"""
Flask web application for Phishing Website Detection System.
Loads the trained model and serves a simple UI where a user pastes a URL
and gets an instant prediction with confidence score.
"""

from flask import Flask, render_template, request, jsonify
import joblib
import pandas as pd

from feature_extraction import extract_features, FEATURE_NAMES

app = Flask(__name__)

model = joblib.load("model/phishing_model.pkl")
feature_names = joblib.load("model/feature_names.pkl")


def predict_url(url: str):
    feats = extract_features(url)
    X = pd.DataFrame([feats], columns=feature_names)
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    confidence = float(max(proba))
    return {
        "url": url,
        "prediction": "Phishing" if pred == 1 else "Legitimate",
        "is_phishing": bool(pred == 1),
        "confidence": round(confidence * 100, 2),
        "features": feats,
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Please enter a URL"}), 400
    result = predict_url(url)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
