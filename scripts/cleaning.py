import pandas as pd
import numpy as np

data = pd.read_csv("../data/processed/clustered5.csv")

# Replace NaN values in the 'speaker' column with 'Patanjali'
data['speaker'] = data['speaker'].replace(np.nan, 'Patanjali')
data['speaker'] = data['speaker'].replace('सञ्जय', 'Sanjay')
data['speaker'] = data['speaker'].replace('धृतराष्ट्र', 'Dhritrashtra')
data['speaker'] = data['speaker'].replace('संजय', 'Sanjay')
data['speaker'] = data['speaker'].replace('भगवान', 'Bhagwan')
data['speaker'] = data['speaker'].replace('अर्जुन', 'Arjun')

print(data['speaker'])
data.to_csv("../data/processed/final.csv")