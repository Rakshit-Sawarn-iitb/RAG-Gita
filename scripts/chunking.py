import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

data = pd.read_csv('../data/processed/expandedGita.csv')
data2 = pd.read_csv('../data/processed/expandedYS.csv')

def chunking_gita(chunks=[]):  
    # Group the data by chapter and verse to handle duplicate entries
    grouped_data = data.groupby(['chapter', 'verse'])
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for (chapter, verse), group in grouped_data:
        # Combine Sanskrit, translations, speakers, and questions for the same verse
        sanskrit = group['sanskrit'].iloc[0]  # Sanskrit is same across rows for the same verse
        translations = list(group['translation'].unique())
        speakers = list(group['speaker'].unique())
        questions = list(group['question'].unique())
        url = f"https://asitis.com/{chapter}/{verse}.html"
        
        purport = None
        retries = 3  # Number of retries allowed
        
        while retries > 0:
            try:
                print(f"Attempting to scrape {url}, retries left: {retries}")
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract the purport from the page
                purport_div = soup.find('div', class_='Purport')
                if purport_div:
                    purport = purport_div.get_text(strip=True)
                    print(f"Purport found for chapter {chapter}, verse {verse}")
                else:
                    purport = translations
                    print(f"Purport not found for chapter {chapter}, verse {verse}")
                
                break  # Exit the retry loop if successful

            except requests.exceptions.RequestException as e:
                print(f"Error scraping {url}: {str(e)}")
                retries -= 1
                if retries > 0:
                    print("Retrying after 10 seconds...")
                    time.sleep(10)
                else:
                    print(f"Failed to scrape {url} after multiple attempts.")
                    purport = translations
        
        chunks.append({
            "id": f"chapter-{chapter}-verse-{verse}",
            "content": {
                "sanskrit": sanskrit,
                "translations": translations,
                "speakers": speakers,
                "questions": questions,
                "purport": purport
            }
        })
        print(f"Processed chapter {chapter}, verse {verse} (BG)")

def chunking_ys(chunks=[]):
    grouped_data = data2.groupby(['chapter', 'verse'])
    for (chapter, verse), group in grouped_data:
        # Combine Sanskrit, translations, speakers, and questions for the same verse
        sanskrit = group['sanskrit'].iloc[0]  # Sanskrit is same across rows for the same verse
        translations = list(group['translation'].unique())
        questions = list(group['question'].unique())
        
        chunks.append({
            "id": f"chapter-{chapter}-verse-{verse}",
            "content": {
                "sanskrit": sanskrit,
                "translations": translations,
                "speakers": "Yoga Sutras",
                "questions": questions,
                "purport": translations
            }
        })
        print(f"Processed chapter {chapter}, verse {verse} (YS)")


def chunking():
    chunks=[]
    chunking_ys(chunks=chunks)
    print(f"Total chunks after Yoga Sutras: {len(chunks)}")
    chunking_gita(chunks=chunks)
    print(f"Total chunks after Bhagavad Gita: {len(chunks)}")
    return chunks

chunks = chunking()
print(f"Total chunks: {len(chunks)}")