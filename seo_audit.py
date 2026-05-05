import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Target website
base_url = "https://www.firstbittech.com/"

# Store data
data = []

# Function to scrape a single page
def scrape_page(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")

        # Title
        title = soup.title.string.strip() if soup.title else "No Title"

        # Meta Description
        meta_desc_tag = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc_tag["content"].strip() if meta_desc_tag else "No Meta Description"

        # Headings
        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]

        # Images Alt Text
        images = soup.find_all("img")
        alt_texts = [img.get("alt", "No Alt") for img in images]

        # Links
        links = soup.find_all("a", href=True)
        internal_links = []

        for link in links:
            href = link["href"]
            full_url = urljoin(base_url, href)
            if base_url in full_url:
                internal_links.append(full_url)

        # Store results
        data.append({
            "URL": url,
            "Title": title,
            "Meta Description": meta_desc,
            "H1 Tags": ", ".join(h1_tags),
            "H2 Tags": ", ".join(h2_tags),
            "Internal Links Count": len(set(internal_links)),
            "Images Missing Alt": len([alt for alt in alt_texts if alt == "No Alt"])
        })

        print(f"Scraped: {url}")

        return list(set(internal_links))

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Crawl multiple pages
visited = set()
to_visit = [base_url]

max_pages = 10  # Limit for safety

while to_visit and len(visited) < max_pages:
    current_url = to_visit.pop(0)

    if current_url not in visited:
        visited.add(current_url)
        new_links = scrape_page(current_url)

        for link in new_links:
            if link not in visited:
                to_visit.append(link)

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("seo_audit.csv", index=False)

print("\nSEO data saved to seo_audit.csv")