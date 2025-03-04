import pandas as pd
import sys
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
from catboost import CatBoostClassifier
from sklearn.preprocessing import LabelEncoder

# By default, a test size of 0.2 is used. See usage to use an additional sys arg to change this
#NOTE: this script does not drop identifiers from the datafram and this should be done in preprocessing
test_size_decimal = 0.2
usage_message = "Usage: python3 <this_script.py> <data.csv> <model_name.json> OPTIONAL:<decimal for test split size, [0 - 1)>"

# Check if the correct number of arguments are provided
if len(sys.argv) != 3 and len(sys.argv) != 4:
    print(usage_message)
    print("Note: only provide the file name, not the path. The csv file must be located in ../data/csv")
    sys.exit(1)  # Exit with error code 1
elif len(sys.argv) == 4:  # valid number of arguments
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
# else: test size is left to 0.2 by default


print(f"Loading CSV File: {sys.argv[1]}")
try:
    df = pd.read_csv(f"../data/csv/{sys.argv[1]}")
    print(f"CSV file loaded")
except FileNotFoundError:
    print(usage_message)
    print(f"ERROR: File '{sys.argv[1]}' not found")
    sys.exit(1)
except Exception as e:
    print(usage_message)
    print(f"ERROR: {e}")
    sys.exit(1)

print(f"Creating X/Y splits and training/testing splits")

# The last column is the label
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values
print(f"X and Y set")

# Need to encode labels to integers
label_encoder = LabelEncoder()
Y_encoded = label_encoder.fit_transform(y)
print(f"Y is encoded")

# Split dataset into training and testing set
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y_encoded, test_size=test_size_decimal, random_state=42)

# Initialize and train model
model = CatBoostClassifier(
    depth=10,                    # should be the same as max depth in xg
    learning_rate=0.1,
    iterations=200,              # should be the same as n_estimators
    l2_leaf_reg=3,               # regularization
    min_child_samples=10,        # should be the same as min_child_samples
    eval_metric='MultiClass',    # mlogloss
    verbose=True                 # otput
)

print(f"Fitting begins...")
model.fit(X_train, Y_train, verbose=True)
print(f"Fit complete!")

# Save model
model.save_model("json/" + sys.argv[2])

# Predictions
print("Testing model with test size of " + str(test_size_decimal))
predictions = model.predict(X_test)

# Evaluation
accuracy = accuracy_score(Y_test, predictions)
f1 = f1_score(Y_test, predictions, average='macro')

print(f"Model Accuracy: {accuracy}")
print(f"F1 Score (Macro Average): {f1}")
