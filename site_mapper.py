#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

def is_internal_link(base_domain, link):
    return urlparse(link).netloc == base_domain

def crawl_site(start_url, max_depth):
    visited = set()
    queue = deque([(start_url, 0)])
    domain = urlparse(start_url).netloc
    found_pages = []

    while queue:
        current_url, depth = queue.popleft()

        if current_url in visited or depth > max_depth:
            continue

        visited.add(current_url)
        found_pages.append(current_url)

        try:
            response = requests.get(current_url, timeout=5)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup.find_all("a", href=True):
                link = urljoin(current_url, tag["href"])
                link = link.split("#")[0]  # remove fragments

                if is_internal_link(domain, link) and link not in visited:
                    queue.append((link, depth + 1))

        except requests.RequestException:
            continue

    return found_pages

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to find all pages on a given website"
    )
    parser.add_argument("url", help="Target URL (e.g. https://example.com)")
    parser.add_argument("-d", "--depth", type=int, default=2, help="Crawl depth (default: 2)")
    parser.add_argument("-o", "--output", help="Save output to file")

    args = parser.parse_args()

    pages = crawl_site(args.url, args.depth)

    for page in pages:
        print(page)

    if args.output:
        with open(args.output, "w") as f:
            for page in pages:
                f.write(page + "\n")
        print(f"\nSaved {len(pages)} pages to {args.output}")

if __name__ == "__main__":
    main()
