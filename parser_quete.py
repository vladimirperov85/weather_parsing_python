
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com"


def get_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 YaBrowser/25.12.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        html = response.text
        
        print(f"HTML загружен из {url}")
        return html
    except Exception as e:
        print("При выполнении запроса произошла ошибка:", e)
        return None
    
def parse_quete(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    all_quetes = soup.find_all("div", class_="quote")
    quotes = {}
    counter = 1
    for quete in all_quetes:
        quete_text = quete.find("span", class_="text").get_text(strip=True)
        quete_author = quete.find("small", class_="author").get_text(strip=True)
        quete_link_author = quete.find("a")["href"]
        full_quete_link_author = urljoin(BASE_URL, quete_link_author)
        tags = {}
        tags_elements = quete.find_all("a", class_="tag")
        for tag in tags_elements:
            tag_text = tag.get_text(strip=True)
            tag_link = tag["href"]
            full_tag_link = urljoin(BASE_URL,tag_link)
            tags[tag_text] = full_tag_link
        quete_data = {
            "text": quete_text,
            "author": quete_author,
            "link_author": quete_link_author,
            "tags": tags
        }
        quotes[str(counter)] = quete_data
        counter += 1
    return quotes


        
if __name__ == "__main__":
    html = get_html(BASE_URL)
    if html:
        quotes = parse_quete(html)
        with open("quotes.json", "w", encoding="utf-8") as f:
            json.dump(quotes, f, ensure_ascii=False, indent=4)
        print("Данные сохранены в quotes.json")
    