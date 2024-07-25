import requests
from bs4 import BeautifulSoup


def scrape_lake_links(base_url, total_pages):
    lake_links = []

    for page in range(1, total_pages + 1):
        url = f"{base_url}?page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to retrieve data for page {page}: Status code {response.status_code}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', {'class': 'list'})
        if not table:
            print(f"No table found on page {page}")
            continue

        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip the header row
            cols = row.find_all('td')
            if len(cols) >= 3:
                item_link = cols[2].find('a')['href'].strip()
                lake_links.append(item_link)

    return lake_links


def main():
    base_url = "https://wldb.ilec.or.jp/Search/listdataitem/199"
    total_pages = 4  # Total number of pages to scrape
    lake_links = scrape_lake_links(base_url, total_pages)

    # Save the result to a text file
    with open('lake_links.txt', 'w') as f:
        for link in lake_links:
            f.write(f"{link}\n")

    print(f"Total links scraped: {len(lake_links)}")


if __name__ == "__main__":
    main()
