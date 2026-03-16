import joblib
import pandas as pd
import traceback

def test():
    try:
        model_pipeline = joblib.load('model.pkl')
        
        input_data = pd.DataFrame([{
            'state': 'Karnataka',
            'company': 'Maruti Suzuki',
            'model': 'Swift',
            'year': 2018,
            'original_price': 800000.0,
            'accident_score': 1,
            'repair_cost': 10000.0,
            'km_driven': 50000.0,
            'fuel_type': 'Petrol'
        }])
        
        pred = model_pipeline.predict(input_data)
        print("Prediction successful:", pred)
    except Exception as e:
        print("Prediction failed:")
        traceback.print_exc()

if __name__ == '__main__':
    test()
