import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

def main():
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, 'dataset.csv')
    
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Please run generate_data.py first.")
        return

    print("Loading dataset...")
    df = pd.read_csv(data_path)
    
    # Define features and target
    target = 'resale_price'
    categorical_features = ['state', 'company', 'model', 'fuel_type']
    numerical_features = ['year', 'original_price', 'accident_score', 'repair_cost', 'km_driven']
    
    X = df[categorical_features + numerical_features]
    y = df[target]
    
    print("Splitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create preprocessing and training pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), categorical_features)
        ],
        remainder='passthrough'
    )
    
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    print("Training RandomForest model...")
    pipeline.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Mean Absolute Error (MAE): {mae:,.2f} INR")
    print(f"R-squared (R2) Score: {r2:.4f}")
    
    # Save the pipeline (includes both preprocessor and model)
    model_path = os.path.join(base_dir, 'model.pkl')
    joblib.dump(pipeline, model_path)
    print(f"Model pipeline saved to {model_path}")
    
    # Generate Feature Importance Plot
    # We need to get feature names after one-hot encoding
    try:
        cat_encoder = pipeline.named_steps['preprocessor'].named_transformers_['cat']
        cat_features_names = cat_encoder.get_feature_names_out(categorical_features)
        
        # In ColumnTransformer remainder='passthrough', the numerical features come after categorical ones
        all_feature_names = list(cat_features_names) + numerical_features
        
        importances = pipeline.named_steps['model'].feature_importances_
        
        # Sort and get top 20
        indices = np.argsort(importances)[::-1]
        top_indices = indices[:20]
        top_features = [all_feature_names[i] for i in top_indices]
        top_importances = importances[top_indices]
        
        plt.figure(figsize=(10, 8))
        plt.title('Top 20 Feature Importances')
        plt.barh(range(len(top_indices)), top_importances[::-1], color='b', align='center')
        plt.yticks(range(len(top_indices)), top_features[::-1])
        plt.xlabel('Relative Importance')
        plt.tight_layout()
        plt.savefig(os.path.join(base_dir, 'feature_importance.png'))
        plt.close()
        print("Saved feature_importance.png")
    except Exception as e:
        print(f"Could not generate feature importance plot: {e}")
        
    # Generate Actual vs Predicted Plot
    plt.figure(figsize=(8, 8))
    plt.scatter(y_test, y_pred, alpha=0.5, color='orange')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=2)
    plt.xlabel('Actual Resale Price (INR)')
    plt.ylabel('Predicted Resale Price (INR)')
    plt.title('Actual vs Predicted Resale Prices')
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, 'actual_vs_predicted.png'))
    plt.close()
    print("Saved actual_vs_predicted.png")
    
    # Save a metrics text file for the backend to read if needed
    with open(os.path.join(base_dir, 'metrics.txt'), 'w') as f:
        f.write(f"R2:{r2:.4f}\n")
        f.write(f"MAE:{mae:,.2f}\n")
    print("Saved metrics.txt")

if __name__ == "__main__":
    main()
