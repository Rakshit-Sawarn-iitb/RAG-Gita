import pandas as pd
import re
data = pd.read_csv('../data/processed/gita_processed1.csv')

def chunking_gita():
    chunks = []
    for _, row in data.iterrows():
        chunks.append({
    "id": f"chapter-{row['Chapter']}-verse-{row['Verse']}",
    "content": {
        "sanskrit": row['Sanskrit '],
        "translations": {
        "Swami Adidevananda": row['Swami Adidevananda'],
        "Swami Gambirananda": row['Swami Gambirananda'],
        "Swami Sivananda": row['Swami Sivananda'],
        "Dr. S. Sankaranarayan": row['Dr. S. Sankaranarayan'],
        "Shri Purohit Swami": row['Shri Purohit Swami']
        },
        "speaker": row['Speaker']
    }
    }
        )
    return chunks

chunkes_gita = chunking_gita()

print(chunkes_gita)