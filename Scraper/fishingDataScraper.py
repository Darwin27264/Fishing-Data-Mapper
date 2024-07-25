import requests
import re
import json
from bs4 import BeautifulSoup


# Function to fetch and save raw HTML for a specific lake
def fetch_and_save_raw_html(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page. Status code: {response.status_code}")
        return None

    raw_html = response.text
    return raw_html


def fetch_lake_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract lake name
    lake_name = soup.find('h2').text.strip() if soup.find('h2') else 'Name not found'

    # Extract location
    location = "Location information not available"
    latitude = None
    longitude = None
    location_tag = soup.find('h3', string=lambda text: text and 'LOCATION' in text)
    if location_tag:
        location_br = location_tag.find_next('br')
        if location_br and location_br.next_sibling and isinstance(location_br.next_sibling, str):
            location = location_br.next_sibling.strip()
            match = re.search(r'(\d+):(\d+)-(\d+):(\d+)N, (\d+):(\d+)-(\d+):(\d+)W', location)
            if match:
                lat_deg1, lat_min1, lat_deg2, lat_min2, lon_deg1, lon_min1, lon_deg2, lon_min2 = map(int,
                                                                                                     match.groups())
                latitude = (lat_deg1 + lat_min1 / 60 + lat_deg2 + lat_min2 / 60) / 2
                longitude = -((lon_deg1 + lon_min1 / 60 + lon_deg2 + lon_min2 / 60) / 2)

    # Extract physical dimensions
    physical_dimensions = {}
    physical_table_tag = soup.find('h3', string=lambda text: text and 'PHYSICAL DIMENSIONS' in text)
    if physical_table_tag:
        physical_table = physical_table_tag.find_next('table')
        if physical_table:
            for row in physical_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    physical_dimensions[key] = value

    # Extract climatic data
    climatic_data = {}
    climatic_table_tag = soup.find('h3', string=lambda text: text and 'CLIMATIC' in text)
    if climatic_table_tag:
        climatic_table = climatic_table_tag.find_next('table')
        if climatic_table:
            for row in climatic_table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 12:
                    month_data = {}
                    for i, month in enumerate(
                            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                        month_data[month] = cells[i].text.strip()
                    climatic_data['Mean Temperature [°C]'] = month_data

    # Extract biological features
    biological_features = {
        'zooplankton': [],
        'benthos': [],
        'fish_species': [],
        'annual_fish_catch': 'Not available'
    }

    bio_section_tag = soup.find('h3', string=lambda text: text and 'BIOLOGICAL FEATURES' in text)
    if bio_section_tag:
        current_section = None
        for element in bio_section_tag.find_all_next(['b', 'br']):
            if element.name == 'b':
                if 'F2 FAUNA' in element.text:
                    current_section = 'fauna'
                elif 'FISHERY PRODUCTS' in element.text:
                    current_section = 'fishery'
                    break
            elif element.name == 'br' and current_section == 'fauna':
                sibling_text = element.next_sibling.strip() if element.next_sibling and isinstance(element.next_sibling,
                                                                                                   str) else ''
                if 'Zooplankton' in sibling_text:
                    biological_features['zooplankton'] = [item.strip() for item in sibling_text.split(';')]
                elif 'Benthos' in sibling_text:
                    biological_features['benthos'] = [item.strip() for item in sibling_text.split(';')]
                elif 'Fish' in sibling_text:
                    fish_br = element.find_next('br')
                    fish_species_list = fish_br.next_sibling.strip().replace('\n',
                                                                             ' ') if fish_br and fish_br.next_sibling and isinstance(
                        fish_br.next_sibling, str) else ''
                    if fish_species_list:
                        biological_features['fish_species'] = [fish.strip() for fish in fish_species_list.split(',')]

    fishery_section = soup.find('b', string=lambda text: text and 'F5 FISHERY PRODUCTS' in text)
    if fishery_section:
        fish_catch_info = fishery_section.find_next('br').next_sibling
        if fish_catch_info and isinstance(fish_catch_info, str):
            match = re.search(r'Annual fish catch \(estimated\): (\d+,\d+ kg)', fish_catch_info)
            if match:
                biological_features['annual_fish_catch'] = match.group(1)

    # Extract water quality data
    water_quality = {}
    transparency_section_tag = soup.find('h3', string=lambda text: text and 'LAKE WATER QUALITY' in text)
    if transparency_section_tag:
        transparency_section = transparency_section_tag.find_next('b', string=lambda
            text: text and 'TRANSPARENCY [m]' in text)
        if transparency_section:
            transparency_table = transparency_section.find_next('table')
            if transparency_table:
                transparency_data = []
                for row in transparency_table.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) == 3:
                        transparency_data.append({
                            'Depth': cells[0].text.strip(),
                            '1972': cells[1].text.strip(),
                            '1975': cells[2].text.strip()
                        })
                water_quality['Transparency'] = transparency_data

    lake_data = {
        'name': lake_name,
        'location': location,
        'latitude': latitude,
        'longitude': longitude,
        'physical_dimensions': physical_dimensions,
        'climatic_data': climatic_data,
        'biological_features': biological_features,
        'water_quality': water_quality
    }

    return lake_data


def main():
    lake_links = []
    with open('lake_links.txt', 'r') as file:
        lake_links = [line.strip() for line in file.readlines()]

    all_lake_data = []

    counter = 0
    for link in lake_links:
        print(str(counter) + ": " + link)
        raw_html = fetch_and_save_raw_html(link)
        if raw_html:
            lake_data = fetch_lake_data(raw_html)
            all_lake_data.append(lake_data)

        counter += 1

    with open('all_lake_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(all_lake_data, json_file, ensure_ascii=False, indent=4)

    print(f"Scraped data for {len(all_lake_data)} lakes and saved to all_lake_data.json")


if __name__ == "__main__":
    main()
