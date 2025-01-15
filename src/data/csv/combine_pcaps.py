import pandas
from sklearn.model_selection import train_test_split

# assumes you have already obtained csvs for each day

print("combining csvs.. no idea how long this is going to take good luck!!!")
print("make sure you give this lots of ram and cpu :)")

# note the lowercase w in wednesday
csv_files = [
    "Monday-WorkingHours.csv",
    "Tuesday-WorkingHours.csv",
    "Wednesday-workingHours.csv",
    "Thursday-WorkingHours.csv",
    "Friday-WorkingHours.csv"
]

train_frames = []
test_frames = []

# pandas assumes the first row of the csv contains column labels, which is true in our case
# so we're fine to just combine them together
for file in csv_files:
    print(f"Reading file {file} !!!")
    dataframe = pandas.read_csv(file)
    dataframe = dataframe.sample(frac=1, random_state=10).reset_index(drop=True)

    # 80/20 training test split
    train_dataframe, test_dataframe = train_test_split(dataframe, test_size=0.2, random_state=10)

    train_frames.append(train_dataframe)
    test_frames.append(test_dataframe)


combined_train_dataframe = pandas.concat(train_frames, ignore_index=True)
combined_test_dataframe = pandas.concat(test_frames, ignore_index=True)

combined_train_dataframe.to_csv("combined_train.csv", index=False)
combined_test_dataframe.to_csv("combined_test.csv", index=False)

print("FINISHED combining!!!! yahoo")