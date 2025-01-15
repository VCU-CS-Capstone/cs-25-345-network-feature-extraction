# This entire file doesn't work right now

import sys

import numpy as np
import pandas as pd

from sklearn.experimental import enable_halving_search_cv # noqa
from sklearn.model_selection import train_test_split, HalvingRandomSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb

usage_message = "Usage: python hyperparameter_tuning_halving.py <filename.csv>"

if len(sys.argv) != 2:
    print(usage_message)
    sys.exit(1)

csv_file = sys.argv[1]
print(f"Loading CSV File: {csv_file}")

# Load csv
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



labels = df.iloc[:, -1].values
le = LabelEncoder()
Y_encoded = le.fit_transform(labels)
df.iloc[:, -1] = Y_encoded


ipv4_source_start, ipv4_source_end = 97, 129
ipv4_destination_start, ipv4_destination_end = 130, 160
ipv4_identification_start, ipv4_identification_end = 33, 48

tcp_source_port_start, tcp_source_port_end = 480, 496
tcp_destination_port_start, tcp_destination_port_end = 496, 512
tcp_sequence_start, tcp_sequence_end = 512, 544
tcp_ack_start, tcp_ack_end = 544, 576

columns_to_remove = [0] + \
                    list(range(ipv4_source_start, ipv4_source_end + 1)) + \
                    list(range(ipv4_destination_start, ipv4_destination_end + 1)) + \
                    list(range(ipv4_identification_start, ipv4_identification_end + 1)) + \
                    list(range(tcp_source_port_start, tcp_source_port_end + 1)) + \
                    list(range(tcp_destination_port_start, tcp_destination_port_end + 1)) + \
                    list(range(tcp_sequence_start, tcp_sequence_end + 1)) + \
                    list(range(tcp_ack_start, tcp_ack_end + 1))

df.drop(df.columns[columns_to_remove], axis=1, inplace=True)

# Separate features (X) and labels (y)
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values
print(f"X and Y set")
print("Shapes: ", X.shape, y.shape)

# Train/test split
test_size_decimal = 0.2
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y_encoded, test_size=test_size_decimal, random_state=42
)

# # Hyperparameters to test for in random search after trial run
# param_distributions = {
#     'max_depth': [3, 5, 7, 10],         # Depth of each tree
#     'learning_rate': [0.01, 0.05, 0.1], # Step size shrinkage
#     'n_estimators': [100, 200, 400],    # Number of trees
#     'gamma': [0, 0.5, 1],              # Min loss reduction
#     'min_child_weight': [1, 5, 10],     # Min sum of instance weight
#     'subsample': [0.8, 1],             # Row sampling
#     'colsample_bytree': [0.8, 1],      # Feature sampling
#     'booster': ['gbtree', 'dart']      # Type of booster
# }

param_distributions = {
    'max_depth': [3, 6, 10],
    'booster': ['gbtree', 'dart'],
    'learning_rate': [0.01, 0.05, 0.1],
    'n_estimators': [300, 500, 800],
    'min_child_weight': [1, 5, 10],
    'gamma': [0, 0.1, 1]
}

# Should i print the length of y encoded unique? what does y encoded even look like?
# what did it look like before getting encoded?
xgb_model = xgb.XGBClassifier(
    objective='multi:softmax',
    num_classes=len(np.unique(Y_encoded)),
    eval_metric='mlogloss',
    random_state=42
)

# WHY DONT THIS WORKBRUH
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

search = HalvingRandomSearchCV(
    estimator=xgb_model,
    param_distributions=param_distributions,
    scoring='accuracy',
    n_jobs=-1,
    factor=2,
    random_state=42,
    cv=cv,
)

print("Starting Halving Random Search...")
search.fit(X_train, Y_train)

# Best parameters
best_params = search.best_params_
best_score = search.best_score_
print(f"Best Parameters: {best_params}")
print(f"Best CV Score: {best_score}")

# Write the best parameters to a file
with open("halving_random_answers.txt", "w") as file:
    file.write("Best Parameters:\n")
    for key, value in best_params.items():
        file.write(f"{key}: {value}\n")
    file.write(f"Best CV Score: {best_score}\n")

# Train model using best parameters
print("Fitting final model with best parameters...")
best_model = xgb.XGBClassifier(
    **best_params,
    eval_metric='mlogloss'
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
