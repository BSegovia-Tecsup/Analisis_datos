"""
datos.py
Uso:
  pip install requests beautifulsoup4 pandas lxml
  python datos.py
"""

import requests, json, time, os
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# ---------------- Configuración ----------------
API_KEY = "AIzaSyDfBoA6NXGOys_xQCjGBCQ9V4f1nQdMDrA"  
CX = "8105881b2d6da4192"  
QUERY = "mujeres en tecnología programadoras"
NUM_PAGES = 3
# ------------------------------------------------

def google_search(query, start):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": API_KEY, "cx": CX, "q": query, "start": start}
    return requests.get(url, params=params, timeout=15).json()

def extract_info(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "lxml")
        title = soup.title.string if soup.title else ""
        desc = soup.find("meta", attrs={"name":"description"})
        desc = desc["content"] if desc and desc.get("content") else ""
        p = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text()) > 40][:3]
        return {"title": title, "description": desc, "paragraphs": p}
    except:
        return {}

def main():
    timestamp = datetime.now().strftime("%H-%M-%S_%d-%m-%Y")
    OUT_JSON = f"salida_{timestamp}.json"
    OUT_CSV = f"salida_{timestamp}.csv"

    results = []
    for page in range(NUM_PAGES):
        data = google_search(QUERY, page * 10 + 1).get("items", [])
        for i, item in enumerate(data, 1):
            url = item["link"]
            print(f"[{page*10+i}] {url}")
            info = extract_info(url)
            results.append({
                "rank": page*10+i,
                "url": url,
                "title_api": item.get("title", ""),
                "snippet_api": item.get("snippet", ""),
                **info
            })
            time.sleep(1) 

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    pd.DataFrame(results).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    print(f"[+] Guardados {len(results)} resultados en {OUT_JSON} y {OUT_CSV}")

if __name__ == "__main__":
    main()
