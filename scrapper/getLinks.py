import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited = set()

def get_all_links(url, base_domain):
    links = set()

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to access {url}: {e}")
        return links

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup.find_all("a", href=True):
        href = tag.get("href")
        full_url = urljoin(url, href)

        parsed = urlparse(full_url)

        # Keep only internal links
        if parsed.netloc == base_domain:
            cleaned_url = parsed.scheme + "://" + parsed.netloc + parsed.path
            links.add(cleaned_url)

    return links


def crawl_website(start_url, max_pages=100):
    base_domain = urlparse(start_url).netloc
    to_visit = [start_url]
    all_links = set()

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)

        if current_url in visited:
            continue

        print(f"Crawling: {current_url}")
        visited.add(current_url)

        links = get_all_links(current_url, base_domain)

        for link in links:
            if link not in visited:
                to_visit.append(link)

        all_links.update(links)

    return all_links


if __name__ == "__main__":
    start_url = "https://abujainvestments.com/"
    links = crawl_website(start_url, max_pages=100)

    # ✅ Save to aiclpages.txt
    with open("aiclpages.txt", "w", encoding="utf-8") as f:
        for link in sorted(links):
            f.write(link + "\n")

    print(f"\n✅ Saved {len(links)} links to aiclpages.txt")