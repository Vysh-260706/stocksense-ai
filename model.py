import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

# LOAD DATASET

df = pd.read_csv("dataset/retail_store_inventory.csv")

# SAMPLE MODEL

numerical_df = df.select_dtypes(include=['int64', 'float64'])

if len(numerical_df.columns) > 1:

    X = numerical_df.iloc[:, :-1]
    y = numerical_df.iloc[:, -1]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestRegressor()

    model.fit(X_train, y_train)

    joblib.dump(model, "inventory_model.pkl")

    print("Model trained successfully")

else:
    print("Dataset does not contain enough numerical columns")