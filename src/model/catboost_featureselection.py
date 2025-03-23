import numpy as np
import pandas as pd
import sys

from sklearn.feature_selection import SelectFromModel
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder

from catboost import CatBoostClassifier, Pool

test_size_decimal = 0.2
usage_message = (
    "Usage: python3 <this_script.py> <data.csv> <model_name.json> OPTIONAL:<decimal for test split size, [0 - 1)>"
)

if len(sys.argv) != 3 and len(sys.argv) != 4:
    print(usage_message)
    print("Note: only provide the file name, not the path. The csv file must be located in ../data/csv")
    sys.exit(1)
elif len(sys.argv) == 4:
    try:
        test_size_decimal = float(sys.argv[3])
        if not 0 <= test_size_decimal < 1:
            print(usage_message)
            print("Test split size must be a decimal value between 0 (inclusive) and 1")
            sys.exit(1)
    except ValueError:
        print(usage_message)
        print("Invalid test split size. Please provide a decimal value between 0 and 1")
        sys.exit(1)

print(f"Loading CSV File: {sys.argv[1]}")
try:
    df = pd.read_csv(f"../data/csv/{sys.argv[1]}")
    print("CSV file loaded")
except FileNotFoundError:
    print(usage_message)
    print(f"ERROR: File '{sys.argv[1]}' not found")
    sys.exit(1)
except Exception as e:
    print(usage_message)
    print(f"ERROR: {e}")
    sys.exit(1)

print("Creating X/Y splits and training/testing splits")
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values
print("X and Y set")

label_encoder = LabelEncoder()
Y_encoded = label_encoder.fit_transform(y)
print("Y is encoded")

X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y_encoded, test_size=test_size_decimal, random_state=42
)

train_pool = Pool(X_train, Y_train)

target_model = sys.argv[2]

model = CatBoostClassifier(
    depth=10,
    learning_rate=0.2,
    iterations=300,
    l2_leaf_reg=1,
    random_strength=1,
    colsample_bylevel=1.0,
    border_count=32,
    min_child_samples=10,
    eval_metric='MultiClass',
    verbose=True
)

print("Fitting begins...")
model.fit(X_train, Y_train)
print("Fit complete!")

model.save_model("json/" + target_model, format="json")

print("Testing model with test size of " + str(test_size_decimal))
predictions = model.predict(X_test)

accuracy = accuracy_score(Y_test, predictions)
f1 = f1_score(Y_test, predictions, average='macro')

print(f"Model Accuracy: {accuracy}")
print(f"F1 Score (Macro Average): {f1}")

feature_importances = model.get_feature_importance(train_pool, type="PredictionValuesChange")

selector = SelectFromModel(
    model,
    threshold=-np.inf,
    max_features=150,
    prefit=True
)

X_train_reduced = selector.transform(X_train)
X_test_reduced = selector.transform(X_test)

print("Original feature size: ", X_train.shape[1])
print("Reduced feature size: ", X_test_reduced.shape[1])

#make a second CatBoost model for the reduced feature set
#this has the hyperparameters I mined
model_reduced = CatBoostClassifier(
    depth=10,
    learning_rate=0.2,
    iterations=300,
    l2_leaf_reg=1,
    min_child_samples=10,
    random_strength=1,
    colsample_bylevel=1.0,
    border_count=32,
    eval_metric='MultiClass',
    verbose=True
)

print("Fitting reduced model...")
model_reduced.fit(X_train_reduced, Y_train)
print("Reduced model fit complete!")

model_reduced.save_model("json/" + target_model + "_reduced", format="json")

print("Testing model with test size of " + str(test_size_decimal))
predictions_reduced = model_reduced.predict(X_test_reduced)

accuracy_reduced = accuracy_score(Y_test, predictions_reduced)
f1_reduced = f1_score(Y_test, predictions_reduced, average='macro')

print(f"Model Accuracy after feature selection: {accuracy_reduced}")
print(f"F1 Score (Macro Average) after feature selection: {f1_reduced}")
