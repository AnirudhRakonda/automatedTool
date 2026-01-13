import argparse
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

def crawl(url, max_pages=30):
    visited = set()
    domain = urlparse(url).netloc

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url)
        page.wait_for_load_state("networkidle")

        links = page.evaluate("""
            () => Array.from(document.querySelectorAll('a'))
                .map(a => a.href)
                .filter(h => h)
        """)

        for link in links:
            if urlparse(link).netloc == domain:
                visited.add(link)

        browser.close()

    return visited

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()

    pages = crawl(args.url)
    for p in pages:
        print(p)

if __name__ == "__main__":
    main()
