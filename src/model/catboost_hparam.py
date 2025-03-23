import numpy as np
import pandas as pd
import sys
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
from catboost import CatBoostClassifier, Pool
from itertools import product

test_size_decimal = 0.2
usage_message = (
    "Usage: python3 <this_script.py> <data.csv> OPTIONAL:<decimal for test split size, [0 - 1)>"
)

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print(usage_message)
    sys.exit(1)
elif len(sys.argv) == 3:
    try:
        test_size_decimal = float(sys.argv[2])
        if not 0 <= test_size_decimal < 1:
            print("Test split size must be a decimal value between 0 (inclusive) and 1")
            sys.exit(1)
    except ValueError:
        print("Invalid test split size. Please provide a decimal value between 0 and 1")
        sys.exit(1)

print(f"Loading CSV File: {sys.argv[1]}")
try:
    df = pd.read_csv(f"../data/csv/{sys.argv[1]}")
    print("CSV file loaded")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("Creating X/Y splits and training/testing splits")
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

label_encoder = LabelEncoder()
Y_encoded = label_encoder.fit_transform(y)

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y_encoded, test_size=test_size_decimal, random_state=42
)

train_pool = Pool(X_train, Y_train)

# Hyperparameter grid
# can try more here, but takes a while on small set so might take a while for large set
depths = [6, 8, 10]
learning_rates = [0.01, 0.1, 0.2]
iterations = [100, 200, 300]
l2_leaf_regs = [1, 3, 5]
random_strengths = [1, 5, 10]
colsample_bylevels = [0.8, 1.0]
border_counts = [32, 64, 128]

best_accuracy = 0
best_params = None
best_model = None

print("Starting hyperparameter tuning...")
for depth, lr, iters, l2_reg, rand_str, colsample, border in product(
    depths, learning_rates, iterations, l2_leaf_regs, random_strengths, colsample_bylevels, border_counts
):
    print(f"Training model with depth={depth}, learning_rate={lr}, iterations={iters}, l2_leaf_reg={l2_reg}, "
          f"random_strength={rand_str}, colsample_bylevel={colsample}, border_count={border}")
    model = CatBoostClassifier(
        depth=depth,
        learning_rate=lr,
        iterations=iters,
        l2_leaf_reg=l2_reg,
        random_strength=rand_str,
        colsample_bylevel=colsample,
        border_count=border,
        min_child_samples=10,
        eval_metric='MultiClass',
        verbose=False
    )
    model.fit(X_train, Y_train)
    predictions = model.predict(X_test)
    accuracy = accuracy_score(Y_test, predictions)
    
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_params = (depth, lr, iters, l2_reg, rand_str, colsample, border)
        best_model = model

print(f"Best Model: depth={best_params[0]}, learning_rate={best_params[1]}, iterations={best_params[2]}, "
      f"l2_leaf_reg={best_params[3]}, random_strength={best_params[4]}, colsample_bylevel={best_params[5]}, "
      f"border_count={best_params[6]}")
print(f"Best Model Accuracy: {best_accuracy}")

if best_model:
    best_model.save_model("json/best_model.json", format="json")
    print("Best model saved!")
