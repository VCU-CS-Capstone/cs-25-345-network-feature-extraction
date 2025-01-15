import pandas
from sklearn.model_selection import train_test_split

# using this to minimize massive combined csv for hyperparameter mining
# this assumes you have combined_train.csv from combine_pcaps.py in this directory

print("opening csv!!!! good luck")

dataframe = pandas.read_csv("combined_train.csv")

y = dataframe.iloc[:, -1]

print("splitting csv now!")
# stratified because iirc there is a large over representation of Ubuntu and Windows systems compared to rest of labels
_, dataframe_small = train_test_split(dataframe, test_size=0.1, random_state=10, stratify=y)

dataframe_small.to_csv("combined_train_small.csv", index=False)

print("done shrinking !!!!")