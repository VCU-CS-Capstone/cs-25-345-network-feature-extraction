import sys
import pandas as pd

from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

import xgboost as xgb

usage_message = "Usage: python hyperparameter_tuning_randomsearch.py <filename.csv>"

if len(sys.argv) != 2:
    print(usage_message)
    sys.exit(1)

csv_file = sys.argv[1]
print(f"Loading CSV File: {csv_file}")

try:
    df = pd.read_csv(f"../data/csv/{csv_file}")
    print(f"CSV file loaded")
except FileNotFoundError:
    print(usage_message)
    print(f"ERROR: File '{csv_file}' not found")
    sys.exit(1)
except Exception as e:
    print(usage_message)
    print(f"ERROR: {e}")
    sys.exit(1)

# Separate features and labels
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values
print(f"X and Y set")
print("Shapes: ", X.shape, y.shape)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
print(f"Y is encoded")

# Train-test split
test_size_decimal = 0.2
X_train, X_test, Y_train, Y_test = train_test_split(
    X, y_encoded, test_size=test_size_decimal, random_state=42
)



# no removal if your dataset already has the identifiers removed

# Define parameters for random search
param_distributions = {
	'max_depth': [3, 5, 7, 10],
	'learning_rate': [0.01, 0.05, 0.1],
	'n_estimators': [100, 300, 500],
	'gamma': [0, 0.5, 1],
	'min_child_weight': [1, 5, 10],
	'subsample': [0.8, 1],
	'colsample_bytree': [0.5, 0.8, 1],
	'booster': ['gbtree', 'dart'],
	'reg_alpha': [0, 0.1, 1],
	'reg_lambda': [1, 2, 5]
}


xgb_model = xgb.XGBClassifier(
    eval_metric='mlogloss',
)

random_search = RandomizedSearchCV(
    estimator=xgb_model,
    param_distributions=param_distributions,
    n_iter=30,             # Number of random parameter sets to try
    # n_iter=1,
    scoring='accuracy',      # Or 'f1_macro', 'f1_weighted' or something else
    n_jobs=-1,
    cv=StratifiedKFold(n_splits=2, shuffle=True, random_state=42),
    verbose=3,               # for logging
    random_state=42
)

# Fit the random search
print("Starting Randomized Search...")
random_search.fit(X_train, Y_train)

# Best parameters
best_params = random_search.best_params_
best_score = random_search.best_score_
print(f"Best Parameters: {best_params}")
print(f"Best CV Score: {best_score}")

# Train final model using best parameters
best_model = xgb.XGBClassifier(
    **best_params,
    eval_metric='mlogloss',
    use_label_encoder=False
)
best_model.fit(X_train, Y_train)

# Evaluate on test set
predictions = best_model.predict(X_test)
accuracy = accuracy_score(Y_test, predictions)
f1 = f1_score(Y_test, predictions, average='macro')

print("\nConfusion Matrix:")
cm = confusion_matrix(Y_test, predictions)
print(cm)

print("\nClassification Report:")
cr = classification_report(Y_test, predictions)
print(cr)

print(f"Final Test Accuracy: {accuracy}")
print(f"Final Test F1 (macro): {f1}")
