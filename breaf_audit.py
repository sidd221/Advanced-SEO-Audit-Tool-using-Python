import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
import time
from collections import Counter
import re

# Type your url here

base_url = "https://www.firstbittech.com"

visited = set()
to_visit = [base_url]
data = []

MAX_PAGES = 15

def get_text_content(soup):
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text(separator=" ")
    return re.sub(r'\s+', ' ', text).strip()

def analyze_page(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        load_time = round(time.time() - start, 2)

        soup = BeautifulSoup(response.text, "lxml")

        # Title
        title = soup.title.string.strip() if soup.title else ""
        
        # Meta Description
        meta_desc = ""
        tag = soup.find("meta", attrs={"name": "description"})
        if tag and tag.get("content"):
            meta_desc = tag["content"]

        # Canonical
        canonical = ""
        canon_tag = soup.find("link", rel="canonical")
        if canon_tag:
            canonical = canon_tag.get("href")

        # Robots
        robots = ""
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        if robots_tag:
            robots = robots_tag.get("content")

        # Headings
        h1 = soup.find_all("h1")
        h2 = soup.find_all("h2")

        # Images
        images = soup.find_all("img")
        missing_alt = sum(1 for img in images if not img.get("alt"))

        # Links
        links = soup.find_all("a", href=True)
        internal, external, broken = 0, 0, 0
        new_links = []

        for link in links:
            href = urljoin(base_url, link["href"])
            if base_url in href:
                internal += 1
                new_links.append(href)
            else:
                external += 1

            try:
                r = requests.head(href, timeout=5)
                if r.status_code >= 400:
                    broken += 1
            except:
                broken += 1

        # Text + Keywords
        text = get_text_content(soup)
        words = text.lower().split()
        word_count = len(words)
        common_keywords = Counter(words).most_common(5)

        # Store
        data.append({
            "URL": url,
            "Title": title,
            "Title Length": len(title),
            "Meta Description": meta_desc,
            "Meta Length": len(meta_desc),
            "H1 Count": len(h1),
            "H2 Count": len(h2),
            "Canonical": canonical,
            "Robots": robots,
            "Images": len(images),
            "Missing Alt": missing_alt,
            "Internal Links": internal,
            "External Links": external,
            "Broken Links": broken,
            "Word Count": word_count,
            "Top Keywords": common_keywords,
            "Load Time (s)": load_time
        })

        print(f"✔ Scraped: {url}")

        return new_links

    except Exception as e:
        print(f"❌ Error: {url} - {e}")
        return []

# Crawl
while to_visit and len(visited) < MAX_PAGES:
    url = to_visit.pop(0)
    if url not in visited:
        visited.add(url)
        links = analyze_page(url)

        for link in links:
            if link not in visited:
                to_visit.append(link)

# Save
df = pd.DataFrame(data)
df.to_csv("advanced_seo_audit.csv", index=False)

print("\n✅ SEO Audit Completed!")