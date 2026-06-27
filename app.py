from flask import Flask, render_template, request, jsonify, redirect
import sqlite3
from datetime import datetime
import joblib
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)

# =======================
# LOAD MODEL & SCALER
# =======================
model = load_model("plant_disease_ann.keras")
scaler = joblib.load("scaler.pkl")

DB_NAME = "predictions.db"

# =======================
# DATABASE INIT
# =======================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            rainfall REAL,
            soil_pH REAL,
            probability REAL,
            risk_percentage REAL,
            risk_level TEXT,
            disease_status TEXT,
            confidence TEXT,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

# =======================
# 🧠 AGENT 1: CONFIDENCE AGENT
# =======================
def confidence_agent(probability):
    p = round(probability, 10)
    if 0.45 <= p <= 0.55:
        return "Low"
    elif p < 0.25 or p > 0.75:
        return "High"
    else:
        return "Medium"

# =======================
# 🧠 AGENT 2: DISEASE STATUS AGENT
# =======================
def disease_agent(probability):
    p = round(probability, 10)
    if p >= 0.25:
        return "Diseased"
    return "Healthy"

# =======================
# 🧠 AGENT 3: RISK DECISION AGENT
# =======================
def decision_agent(probability):
    p = round(probability, 10)
    if p >= 0.35:
        return {
            "status": "High Risk",
            "color": "red",
            "recommendations": [
                "Apply fungicide immediately",
                "Isolate infected plants",
                "Reduce irrigation",
                "Remove infected leaves"
            ]
        }
    elif p >= 0.25:
        return {
            "status": "Moderate Risk",
            "color": "orange",
            "recommendations": [
                "Monitor plant condition daily",
                "Improve drainage system",
                "Avoid overwatering",
                "Apply preventive spray"
            ]
        }
    else:
        return {
            "status": "Low Risk",
            "color": "green",
            "recommendations": [
                "Plant is healthy",
                "Maintain current care",
                "Ensure proper sunlight",
                "Routine monitoring"
            ]
        }

# =======================
# INTEGRATION: All agents pipeline
# =======================
def run_all_agents(probability):
    disease_status = disease_agent(probability)
    confidence     = confidence_agent(probability)
    decision       = decision_agent(probability)
    return {
        "disease_status":  disease_status,
        "confidence":      confidence,
        "status":          decision["status"],
        "color":           decision["color"],
        "recommendations": decision["recommendations"]
    }

# =======================
# DATABASE HELPERS
# =======================
def save_to_db(temperature, humidity, rainfall, soil_pH,
               probability, risk_percentage, decision, disease_status, confidence):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO prediction_history
        (temperature, humidity, rainfall, soil_pH,
         probability, risk_percentage, risk_level,
         disease_status, confidence, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        temperature,
        humidity,
        rainfall,
        soil_pH,
        probability,
        risk_percentage,
        decision["status"],
        disease_status,
        confidence,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def get_all_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT temperature, humidity, rainfall, soil_pH,
               disease_status,
               ROUND(probability * 100, 2) as risk_percentage,
               risk_level,
               confidence,
               date
        FROM prediction_history
        ORDER BY id DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows


def clear_all_history():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM prediction_history")
    conn.commit()
    conn.close()

# =======================
# ROUTES
# =======================
@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/history")
def history():
    try:
        rows = get_all_history()
        return render_template("history.html", rows=rows)
    except Exception as e:
        return render_template("history.html", rows=[], error=str(e)), 200


@app.route("/delete-history", methods=["POST"])
def delete_history():
    try:
        clear_all_history()
        return redirect("/history")
    except Exception as e:
        return redirect("/history")


# =======================
# PREDICTION API
# =======================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        # ===== Validate Input =====
        required_fields = ["temperature", "humidity", "rainfall", "soil_pH"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        temperature = float(data["temperature"])
        humidity    = float(data["humidity"])
        rainfall    = float(data["rainfall"])
        soil_pH     = float(data["soil_pH"])

        # ===== Model Prediction =====
        X        = np.array([[temperature, humidity, rainfall, soil_pH]])
        X_scaled = scaler.transform(X)

        probability     = float(model.predict(X_scaled)[0][0])
        risk_percentage = round(probability * 100, 2)

        print("Input:", X)
        print("Scaled:", X_scaled)
        print("ANN Probability:", probability)

        # ===== Run All Agents =====
        result = run_all_agents(probability)

        # ===== Save to Database =====
        decision = decision_agent(probability)
        save_to_db(
            temperature, humidity, rainfall, soil_pH,
            probability, risk_percentage,
            decision,
            result["disease_status"],
            result["confidence"]
        )

        # ===== Response =====
        return jsonify({
            "status":          result["status"],
            "disease_status":  result["disease_status"],
            "risk_percentage": risk_percentage,
            "color":           result["color"],
            "confidence":      result["confidence"],
            "recommendations": result["recommendations"]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =======================
# HEALTH CHECK (for testing)
# =======================
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# =======================
# MAIN
# =======================

# Runs always — ensures DB table exists whether started via
# "python app.py", pytest, or any WSGI/test runner
init_db()

if __name__ == "__main__":
    app.run(debug=True)