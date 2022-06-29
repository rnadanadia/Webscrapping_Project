import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pandas as pd
import schedule
import datetime
import time


headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}

driver = webdriver.Safari()

property_types = []
prices = []
zipcodes = []
bedrooms = []
bathrooms = []
living_areas = []
equipped_kitchens = []
furnisheds = []
garden_surfaces = []
surface_plots = []
building_conditions = []
energy_classes = []


def get_property(links):
    req = requests.get(links, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    property_info = soup.find('h1', {'class':'classified__title'})
    property = " ".join(re.findall(r'[A-Za-z]+', property_info.text))
    property = property.replace("for sale", "")
    property_types.append(property)
    print("Property type: ", property_types[-1])
    return

def get_price(links):
    req = requests.get(links, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    every_price = soup.find('span', {'class':'sr-only'}).text
    #print(every_price)
    price = re.findall(r'[\d]+', every_price)[0]
    prices.append(price)
    print("Price: ", price)
    return

def get_zipcode(links):
    driver.get(links)
    # req = requests.get(links, headers)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    address_rows = soup.find('div', {'class':'classified__information--address'}).text
    zipcode = " ".join(re.findall(r'[\d+]{4}', address_rows))
    zipcodes.append(zipcode)
    print("Zipcode: ", zipcodes[-1])
    return
    
#bedroom, bathroom, living_area, equipped kitchen, furnished
#garden surface, surface plots, building conditions, energy classes
def get_the_rest(links):
    req = requests.get(links, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    
    classified_table_rows = soup.find_all('tr', {'class':'classified-table__row'})
    
    bedrooms.append(classified_table_data(classified_table_rows, 'Bedrooms'))
    bathrooms.append(classified_table_data(classified_table_rows, 'Bathrooms'))
    living_areas.append(classified_table_data(classified_table_rows, 'Living area'))
    equipped_kitchens.append(classified_table_data(classified_table_rows, 'Kitchen type'))
    furnisheds.append(classified_table_data(classified_table_rows, 'Furnished'))
    garden_surfaces.append(classified_table_data(classified_table_rows, 'Garden surface'))
    surface_plots.append(classified_table_data(classified_table_rows, 'Surface of the plot'))
    building_conditions.append(classified_table_data(classified_table_rows, 'Building condition'))
    energy_classes.append(classified_table_data(classified_table_rows, 'Energy class'))
    return

def classified_table_data(classified_table_rows, target):
    for table_rows in classified_table_rows:
        table_row = table_rows.find('th', {'class': 'classified-table__header'})
        if table_row != None:
            if target in table_row.string:
                answer = table_rows.find('td', {'class':'classified-table__data'})
                if answer != None:
                    return answer.find(text=True).strip()
    return None
    
counts = 0
for i in range(1,2):
    url = f'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={i}&orderBy=relevance'
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    for pages in soup.find_all('li', {'class':'search-results__item'}):
        for links in pages.find_all('a', {'class':'card__title-link'}):
            counts += 1
            print(f'page number: {i}, click count: {counts}')
            print(links['href'])
            get_price(links["href"])
            get_property(links["href"])
            get_zipcode(links["href"])
            get_the_rest(links["href"])

         
df = pd.DataFrame()

df["property_types"] = property_types
df["prices"] = prices
df["zipcodes"] = zipcodes
df["bedrooms"] = bedrooms
df["bathrooms"] = bathrooms
df["living_areas (m2)"] = living_areas
df["equipped_kitchens"] = equipped_kitchens
df["furnisheds"] = furnisheds
df["garden_surfaces (m2)"] = garden_surfaces
df["surface_plots (m2)"] = surface_plots
df["building_conditions"] = building_conditions
df["energy_classes"] = energy_classes

df.to_csv("web_scrapping.csv", mode = "w", header=True)
