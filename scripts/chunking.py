import pandas as pd

data = pd.read_csv('../data/processed/expandedGita.csv')

def chunking_gita():
    chunks = []
    
    # Group the data by chapter and verse to handle duplicate entries
    grouped_data = data.groupby(['chapter', 'verse'])
    
    for (chapter, verse), group in grouped_data:
        # Combine Sanskrit, translations, speakers, and questions for the same verse
        sanskrit = group['sanskrit'].iloc[0]  # Sanskrit is same across rows for the same verse
        translations = list(group['translation'].unique())
        speakers = list(group['speaker'].unique())
        questions = list(group['question'].unique())
        
        chunks.append({
            "id": f"chapter-{chapter}-verse-{verse}",
            "content": {
                "sanskrit": sanskrit,
                "translations": translations,
                "speakers": speakers,
                "questions": questions,
            }
        })
    
    return chunks

chunks = chunking_gita()