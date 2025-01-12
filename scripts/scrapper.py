import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

data =pd.read_csv('../data/processed/clustered4.csv')

#Function to scrape commentaries from https://asitis.com
def scrape():
    purports = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for i in range(len(data)):
        if data['Source'][i] == 'Gita':
            chapter = data['chapter'][i]
            verse = data['verse'][i]
            url = f"https://asitis.com/{chapter}/{verse}.html"
            retries = 3
            #incase scraping fails
            while retries > 0:
                try:
                    print(f"Attempting to scrape {url}, retries left: {retries}")
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    purport_div = soup.find('div', class_='Purport')
                    if purport_div:
                        purport = purport_div.get_text(strip=True)
                        print(f"Purport found for chapter {chapter}, verse {verse}")
                    else:
                        purport = data['translation'][i]
                        print(f"Purport not found for chapter {chapter}, verse {verse}")
                    purports.append(purport)
                    break
                except requests.exceptions.RequestException as e:
                    print(f"Error scraping {url}: {str(e)}")
                    retries -= 1
                    if retries > 0:
                        print("Retrying after 10 seconds...")
                        time.sleep(10)
                    else:
                        purports.append(data['translation'][i])
        else:
            purports.append(data['translation'][i])
    #adding it to dataset
    data['purport'] = purports
    data.to_csv('../data/processed/clustered5.csv', index=False)
    print("Done with scraping")

if __name__ == '__main__':
    print("Starting scraping")
    scrape()