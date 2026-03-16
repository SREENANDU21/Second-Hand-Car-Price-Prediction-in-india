from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import os

app = Flask(__name__)

# Base path
base_dir = os.path.dirname(__file__)

# Load model
model_path = os.path.join(base_dir, 'model.pkl')
try:
    model_pipeline = joblib.load(model_path)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model_pipeline = None

# Single source of truth for dropdowns (same as generate_data.py)
states = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", 
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", 
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", 
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", 
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

uts = [
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu", 
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]

car_data = {
    "Maruti Suzuki": ["Swift", "Baleno", "Dzire", "Ertiga"],
    "Hyundai": ["i20", "Creta", "Venue", "Verna"],
    "Tata": ["Nexon", "Tiago", "Harrier", "Safari"],
    "Mahindra": ["Thar", "XUV700", "Scorpio-N", "Bolero"],
    "Honda": ["City", "Amaze", "Elevate"],
    "Toyota": ["Fortuner", "Innova Crysta", "Urban Cruiser Hyryder"],
    "Kia": ["Seltos", "Sonet", "Carens"],
    "Volkswagen": ["Taigun", "Virtus", "Polo"],
    "Skoda": ["Kushaq", "Slavia", "Octavia"],
    "MG": ["Hector", "Astor"]
}

fuel_types = ["Petrol", "Diesel"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/options', methods=['GET'])
def get_options():
    return jsonify({
        "locations": states + uts,
        "companies_and_models": car_data,
        "fuel_types": fuel_types
    })

@app.route('/predict', methods=['POST'])
def predict():
    if not model_pipeline:
        return jsonify({"error": "Model not loaded on the server"}), 500
        
    try:
        data = request.json
        state = data.get('state')
        company = data.get('company')
        model = data.get('model')
        year = int(data.get('year'))
        original_price = float(data.get('original_price'))
        accident_score = int(data.get('accident_score', 1))
        repair_cost = float(data.get('repair_cost', 0))
        km_driven = float(data.get('km_driven'))
        fuel_type = data.get('fuel_type')
        
        # Create a dataframe for the input
        input_data = pd.DataFrame([{
            'state': state,
            'company': company,
            'model': model,
            'year': year,
            'original_price': original_price,
            'accident_score': accident_score,
            'repair_cost': repair_cost,
            'km_driven': km_driven,
            'fuel_type': fuel_type
        }])
        
        # Predict using the pipeline
        predicted_price = model_pipeline.predict(input_data)[0]
        
        # Ensure non-negative
        predicted_price = max(10000, predicted_price)
        
        # Round 
        predicted_price = round(predicted_price)
        
        return jsonify({
            "predicted_price": predicted_price,
            "currency": "INR"
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

@app.route('/metrics', methods=['GET'])
def get_metrics():
    metrics_path = os.path.join(base_dir, 'metrics.txt')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            lines = f.readlines()
            metrics = {}
            for line in lines:
                if ':' in line:
                    key, val = line.strip().split(':', 1)
                    metrics[key] = val
            return jsonify(metrics)
    return jsonify({"error": "Metrics not found"}), 404

if __name__ == '__main__':
    from waitress import serve
    print("Serving on http://127.0.0.1:5000 ...")
    serve(app, host='127.0.0.1', port=5000)
