import requests
from bs4 import BeautifulSoup
import os

def scrape_passport_stamps(url, output_folder="presentation/stamps"):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing passport stamps. Looking for tables with class 'wikitable'
    # and then checking for 'Entry Stamp' in the header.
    table = None
    for t in soup.find_all("table", class_="wikitable"):
        if t.find("th", string="Entry Stamp"):
            table = t
            break

    if not table:
        print("Error: Could not find the table with passport stamp information.")
        return

    image_links = []
    # Assuming the first row is the header
    rows = table.find_all("tr")[1:]

    for row in rows:
        cols = row.find_all("td")
        if len(cols) > 1:
            country_name_tag = cols[0].find("a")
            country_name = country_name_tag.text if country_name_tag else "Unknown"

            # Entry Stamp is typically in the second column (index 1)
            entry_stamp_col = cols[1]
            entry_img_tag = entry_stamp_col.find("img")
            if entry_img_tag and entry_img_tag.has_attr("src"):
                img_src = entry_img_tag["src"]
                if img_src.startswith("//"):
                    img_src = "https:" + img_src
                image_links.append({"country": country_name, "type": "entry", "url": img_src})

            # Exit Stamp is typically in the third column (index 2)
            if len(cols) > 2:
                exit_stamp_col = cols[2]
                exit_img_tag = exit_stamp_col.find("img")
                if exit_img_tag and exit_img_tag.has_attr("src"):
                    img_src = exit_img_tag["src"]
                    if img_src.startswith("//"):
                        img_src = "https:" + img_src
                    image_links.append({"country": country_name, "type": "exit", "url": img_src})
    
    # Download images
    for link_info in image_links:
        img_url = link_info["url"]
        country = link_info["country"]
        stamp_type = link_info["type"]
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            img_response = requests.get(img_url, stream=True, headers=headers)
            img_response.raise_for_status()
            
            # Extract filename from URL or create a new one
            filename = os.path.join(output_folder, f"{country.replace(' ', '_')}_{stamp_type}_{os.path.basename(img_url.split('/')[-1])}")
            
            with open(filename, 'wb') as f:
                for chunk in img_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {filename}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {img_url}: {e}")

if __name__ == "__main__":
    wiki_url = "https://commons.wikimedia.org/wiki/Passport_stamps_by_country_or_territory"
    scrape_passport_stamps(wiki_url)
