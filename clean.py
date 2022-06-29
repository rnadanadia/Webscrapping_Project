import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

prices = []
zipcodes = []
localities = []
property_types = []
bedrooms = []
bathrooms = []
living_areas = []
equipped_kitchens = []
furnisheds = []
garden_surfaces = []
surface_plots = []
building_conditions = []
energy_classes = []

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
}

driver = webdriver.Safari()

def get_info(links):
    req = requests.get(links, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    #soup = BeautifulSoup(driver.page_source, "lxml")

    allrows = soup.find_all('tr', {'class': 'classified-table__row'})

    bedrooms.append(add_attr(allrows, "Bedrooms"))
    bathrooms.append(add_attr(allrows, "Bathrooms"))
    living_areas.append(add_attr(allrows, "Living area"))
    equipped_kitchens.append(add_attr(allrows, "Equipped kitchen"))
    furnisheds.append(add_attr(allrows, "Furnished"))
    garden_surfaces.append(add_attr(allrows, "Garden surface"))
    surface_plots.append(add_attr(allrows, "Surface of the plot"))
    building_conditions.append(add_attr(allrows, "Building condition"))
    energy_classes.append(add_attr(allrows, "Energy Class"))


def add_attr(allrows, target):
    for row in allrows:
        header = row.find('th', {'class': 'classified-table__header'})
        if header is not None:
            if target in header.string:
                answer = row.find('td', {'class': 'classified-table__data'})
                if answer is not None:
                    return answer.find(text=True).strip()
    return None

counts = 0
for i in range(1, 2):
    url = f'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={i}&orderBy=relevance'
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    for pages in soup.find_all('li', {'class': 'search-results__item'}):
        for links in pages.find_all('a', {'class': 'card__title-link'}):
            counts += 1
            print(f'page number: {i}, click count: {counts}')
            print(links['href'])
            get_info(links["href"])

df = pd.DataFrame()

df["property_types"] = property_types
df["bedrooms"] = bedrooms
df["bathrooms"] = bathrooms
df["living_areas"] = living_areas
df["equipped_kitchens"] = equipped_kitchens
df["furnisheds"] = furnisheds
df["garden_surfaces"] = garden_surfaces
df["surface_plots"] = surface_plots
df["building_conditions"] = building_conditions
df["energy_classes"] = energy_classes

df.to_csv("web_scrapping.csv", mode="w", header=True)
