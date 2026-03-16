import requests

url = "http://127.0.0.1:5000/predict"

payload = {
    "state": "", # empty string because user didn't change dropdown
    "company": "Maruti Suzuki",
    "model": "Swift",
    "year": "2018",
    "original_price": "800000",
    "km_driven": "50000",
    "fuel_type": "Petrol",
    "accident_score": "1",
    "repair_cost": "010000"
}

try:
    response = requests.post(url, json=payload)
    print("Response Status:", response.status_code)
    print("Response JSON:", response.json())
except Exception as e:
    print("Request failed:", e)
