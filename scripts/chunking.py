import pandas as pd

# Read the processed data
data = pd.read_csv('../data/processed/final.csv')

#Chunking the whole dataset verse-wise
def chunking(): 
    chunks = []
    for i in range(len(data)):   
        row = data.iloc[i]
        cluster_content = {
            "chapter": row['chapter'],
            "verse": row['verse'],
            "source": row['Source'],
            "sanskrit": row['sanskrit'],
            "translations": row['translation'],
            "speakers": row['speaker'],
            "questions": row['question'],
            "purports": row['purport']
        }
        chunks.append(cluster_content)
    
    return chunks