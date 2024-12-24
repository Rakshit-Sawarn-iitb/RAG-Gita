import pandas as pd
data = pd.read_csv('../data/processed/gita_processed1.csv')

def chunking_gita():
    chunks = []
    for _, row in data.iterrows():
        chunks.append({
    "id": f"chapter-{row['Chapter']}-verse-{row['Verse']}",
    "content": {
        "sanskrit": row['Sanskrit '],
        "translations": {
        "Swami Adidevananda": row['Swami Adidevananda']
        },
        "speaker": row['Speaker']
    }
    }
        )
    return chunks