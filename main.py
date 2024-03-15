import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import codecs

import re
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pymongo
from bs4 import BeautifulSoup
import pageSource

# url = "https://www.redweek.com/resort/P52-morritts-grand-resort"
#
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["Timeshare_Exchange_Platform"]
mycol = mydb["resorts"]

# response = requests.get(url)
soup = BeautifulSoup(pageSource.source, "html.parser")

name = soup.find('div', class_='resort-header--home').find('h1')
location = soup.find('div', class_='resort-header--home').find('h4')
img_elements = soup.find('div', class_='resort-header--home').find_all('img')
description = soup.find('div', class_='resort-description')

# FEATURES OF RESORT
h2_tag = soup.find('h2', string='On-Site Features & Amenities')
ul_tag = h2_tag.find_next('ul')
li_items = ul_tag.find_all('li')
facilities = [li_item.text for li_item in li_items]

# NEARBY ATTRACTION
h2_tag = soup.find('h2', string='Nearby Attractions')
ul_tag = h2_tag.find_next('ul')
li_items = ul_tag.find_all('li')
nearby_attraction = [li_item.text.strip() for li_item in li_items]

# FINDING POLICIES OF RESORT
h2_tag = soup.find('h2', string='Policies')
ul_tag = h2_tag.find_next('ul')
li_items = ul_tag.find_all('li')
policies = [li_item.text for li_item in li_items]

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# driver.get(url)
# open_gallery_button = driver.find_element(By.CLASS_NAME, 'open-gallery')
# open_gallery_button.click()
# wait = WebDriverWait(driver, 2)
# wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'lazy')))
# updated_html = driver.page_source
# driver.quit()
#
# # Parse the updated HTML with BeautifulSoup
# soup_updated = BeautifulSoup(updated_html, "html.parser")

img_full = soup.findAll('a', class_='slick-anchor')
image_urls = [a['href'] for a in img_full]

# Find all unit-type divs
unit_type_divs = soup.find_all('div', class_='unit-type')

# List to store room objects
room_types = []

# Iterate through each unit-type div
for unit_type_div in unit_type_divs:
    # Extract relevant information
    roomName = unit_type_div.find('h3', class_='mb-1').text.strip()
    details = unit_type_div.find('p', class_='mb-2').text.strip()
    img_url = unit_type_div.find('img')['data-src']
    # Create a dictionary for each room type
    room_type_obj = {'name': roomName, 'details': details, 'img': img_url}
    # Append the dictionary to the list
    room_types.append(room_type_obj)

print(name.text)
print(location.text)
print(description.text)
print(facilities)
print(nearby_attraction)
print(policies)
print(room_types)
print(image_urls)
# Define a MongoDB document schema with trimmed strings

resort_data = {
    "name": name.text.strip(),
    "location": location.text.strip(),
    "description": description.text.strip(),
    "facilities": [facility.strip() for facility in facilities],
    "nearby_attractions": [attraction.strip() for attraction in nearby_attraction],
    "policies": [policy.strip() for policy in policies],
    "image_urls": image_urls[:10],
    "unit": room_types
}

# Insert the document into the MongoDB collection
# mycol.insert_one(resort_data)

print("Resort data inserted into MongoDB successfully!")

mycol_resorts = mydb["resorts"]
mycol_units = mydb["units"]

# Assuming you have retrieved data about the resort and units from your scraping logic

# Extracted resort data
resort_data = {
    "name": name.text.strip(),
    "location": location.text.strip(),
    "description": description.text.strip(),
    "facilities": [facility.strip() for facility in facilities],
    "nearby_attractions": [attraction.strip() for attraction in nearby_attraction],
    "policies": [policy.strip() for policy in policies],
    "image_urls": image_urls[:10]
}

# Insert the resort document into the MongoDB collection
resort_id = mycol_resorts.insert_one(resort_data).inserted_id

# Extracted unit data
unit_data_list = []

for room_type in room_types:
    unit_data = {
        "name": room_type['name'],
        "details": room_type['details'],
        "image_urls": [room_type['img']],
        "resort": resort_id  # Reference to the resort's object ID
    }
    unit_id = mycol_units.insert_one(unit_data).inserted_id
    unit_data_list.append(unit_id)

# Update the resort document to include references to the unit object IDs
mycol_resorts.update_one({"_id": resort_id}, {"$set": {"units": unit_data_list}})

print("Resort data with associated units inserted into MongoDB successfully!")
