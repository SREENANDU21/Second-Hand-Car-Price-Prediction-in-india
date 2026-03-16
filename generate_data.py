import pandas as pd
import numpy as np
import random
import os

# Define the states and union territories
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

all_locations = states + uts

# Define car companies and models with base original prices (approx median prices in INR)
car_data = {
    "Maruti Suzuki": {"models": {"Swift": 700000, "Baleno": 850000, "Dzire": 800000, "Ertiga": 1100000}, "dep_rate": 0.05},
    "Hyundai": {"models": {"i20": 900000, "Creta": 1500000, "Venue": 1100000, "Verna": 1300000}, "dep_rate": 0.06},
    "Tata": {"models": {"Nexon": 1200000, "Tiago": 650000, "Harrier": 2000000, "Safari": 2200000}, "dep_rate": 0.07},
    "Mahindra": {"models": {"Thar": 1600000, "XUV700": 2100000, "Scorpio-N": 1900000, "Bolero": 1000000}, "dep_rate": 0.065},
    "Honda": {"models": {"City": 1400000, "Amaze": 900000, "Elevate": 1500000}, "dep_rate": 0.055},
    "Toyota": {"models": {"Fortuner": 4000000, "Innova Crysta": 2500000, "Urban Cruiser Hyryder": 1600000}, "dep_rate": 0.04},
    "Kia": {"models": {"Seltos": 1600000, "Sonet": 1200000, "Carens": 1400000}, "dep_rate": 0.06},
    "Volkswagen": {"models": {"Taigun": 1500000, "Virtus": 1400000, "Polo": 900000}, "dep_rate": 0.08},
    "Skoda": {"models": {"Kushaq": 1500000, "Slavia": 1400000, "Octavia": 3000000}, "dep_rate": 0.08},
    "MG": {"models": {"Hector": 1900000, "Astor": 1400000}, "dep_rate": 0.09}
}

fuel_types = ["Petrol", "Diesel"]

def generate_record():
    state = random.choice(all_locations)
    company = random.choice(list(car_data.keys()))
    model = random.choice(list(car_data[company]["models"].keys()))
    
    # Original Base Price + some noise (+- 15%)
    base_price = car_data[company]["models"][model]
    original_price = int(base_price * random.uniform(0.85, 1.15))
    
    year = random.randint(2010, 2023)
    age = 2024 - year
    
    km_driven = random.randint(5000, 250000)
    
    accident_score = random.randint(1, 10)  # 1 = clean, 10 = total loss
    
    # Repair cost (more likely to be zero if accident score is low)
    if accident_score <= 2:
        repair_cost = random.randint(0, 5000)
    elif accident_score <= 5:
        repair_cost = random.randint(5000, 50000)
    elif accident_score <= 8:
        repair_cost = random.randint(50000, 200000)
    else:
        repair_cost = random.randint(100000, 500000)
        
    # Cap repair cost
    if repair_cost > original_price * 0.5:
        repair_cost = int(original_price * 0.5)

    fuel_type = random.choice(fuel_types)
    
    if fuel_type == "Diesel" and model in ["Swift", "Baleno", "Tiago", "Amaze", "Polo"]:
        # Small hatchbacks/compact cars often come mainly in Petrol now, let's just leave it or swap some
        fuel_type = "Petrol"

    # Resale Price Logic
    # 1. Base depreciation by age
    depreciation_rate = car_data[company]["dep_rate"]
    # Diesel cars depreciate faster
    if fuel_type == "Diesel":
        depreciation_rate += 0.01 
        
    value_retention = (1 - depreciation_rate) ** age
    
    # 2. Penalty for km_driven
    # Average ~ 10,000 km per year. Extra km penalties.
    expected_km = age * 10000
    excess_km = max(0, km_driven - expected_km)
    km_penalty = (excess_km / 10000) * 0.015  # 1.5% off per extra 10k kms
    
    # 3. Accident Penalty
    # Every point of accident score beyond 1 hits value by ~2.5%
    accident_penalty = (accident_score - 1) * 0.025
    
    # 4. Repair Penalty
    # Just observing repair cost decreases perceived value somewhat beyond the actual cost
    repair_penalty = (repair_cost / original_price) * 0.5 
    
    total_retention = value_retention - km_penalty - accident_penalty - repair_penalty
    
    # Floor at 10% of original price
    total_retention = max(0.10, total_retention)
    
    # Add random sentiment noise (+- 5%)
    total_retention *= random.uniform(0.95, 1.05)
    
    resale_price = int(original_price * total_retention)
    
    # Round off to nearest 1000 for realistic looking prices
    resale_price = round(resale_price, -3)
    original_price = round(original_price, -3)
    repair_cost = round(repair_cost, -2)

    return {
        "state": state,
        "company": company,
        "model": model,
        "year": year,
        "original_price": original_price,
        "accident_score": accident_score,
        "repair_cost": repair_cost,
        "km_driven": km_driven,
        "fuel_type": fuel_type,
        "resale_price": resale_price
    }

def main():
    num_records = 3500
    records = []
    
    print(f"Generating {num_records} realistic used car records...")
    for _ in range(num_records):
        records.append(generate_record())
        
    df = pd.DataFrame(records)
    
    output_path = os.path.join(os.path.dirname(__file__), 'dataset.csv')
    df.to_csv(output_path, index=False)
    
    print(f"Dataset generated and saved to {output_path}")
    print(df.head())
    print("\nDataset Info:")
    print(df.info())

if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    main()
