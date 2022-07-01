
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pandas as pd
import sqlite3
from pandasql import sqldf
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

primary_keys = []
property_types = []
prices = []
street_names = []
zipcodes = []
localities = []
bedrooms = []
bathrooms = []
living_areas = []
equipped_kitchens = []
furnisheds = []
garden_surfaces = []
surface_plots = []
building_conditions = []
energy_classes = []



def get_property_and_primary_keys(links):
    property = links.split('/')[5]  
    property_types.append(property)
    
    primary_key_link = links.split('/')[-1]
    primary_key = primary_key_link.split('?')[0] 
    primary_keys.append(primary_key)
    print("Primary key: ", primary_keys[-1])
    print("Property type: ", property_types[-1])
    return


def get_price(soup):
    class_price = soup.find('p', {'class': 'classified__price'})
    if class_price is not None:
        every_price = class_price.find('span', {'class':'sr-only'}).text
        if every_price is not None:
            price = (re.findall(r'[\d]+', every_price)[0])
            prices.append(price)
            print("Price: ", price)
        else:
            prices.append(None)
    else:
        prices.append(None)


def get_address(soup):
    address_rows = soup.find('div', {'class':'classified__information--address'})
    if address_rows is not None:
        address_row = address_rows.find_all('span', {'class': 'classified__information--address-row'})
        if address_row is not None:
            if len(address_row)==2:
                street_name = address_row[0].text.strip()
                street_names.append(street_name)
                zipcode_and_locality = address_row[1].text.strip().split('—')
                zipcode = zipcode_and_locality[0].strip()
                locality = zipcode_and_locality[-1].strip()
                localities.append(locality)
                zipcodes.append(zipcode) 
                print("Street name:" ,street_name)
                print("Zipcode: ", zipcode)
                print("Locality: ", locality)
            else: 
                zipcode_and_locality = address_row[0].text.strip().split('—')
                zipcode = zipcode_and_locality[0].strip()
                zipcodes.append(zipcode)
                locality = zipcode_and_locality[-1].strip
                localities.append(locality)
                street_names.append(None)
                print("Zipcode: ", zipcode)
                print("Locality: ", locality)
                return
        else:
            street_names.append(None)
            zipcodes.append(None)
            localities.append(None)
            street_names.append(None)
    else:
        street_names.append(None)
        zipcodes.append(None)
        localities.append(None)
        street_names.append(None)

def get_the_rest(soup):
    
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
        if table_row is not None:
            if target in table_row.string:
                answer = table_rows.find('td', {'class':'classified-table__data'})
                if answer is not None:
                    return answer.find(text=True).strip()
    return None

counts = 0
for i in range(1,11):
    url = f'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={i}&orderBy=relevance'
    driver.get(url)
    mainsoup = BeautifulSoup(driver.page_source, 'lxml')
    for pages in mainsoup.find_all('li', {'class':'search-results__item'}):
        for links in pages.find_all('a', {'class':'card__title-link'}):
            counts += 1
            print(f'page number: {i}, click count: {counts}')
            print(links['href'])
            driver.get(links['href'])
            soup = BeautifulSoup(driver.page_source, 'lxml')
            get_property_and_primary_keys(links["href"])
            get_price(soup)
            get_address(soup)
            get_the_rest(soup)

            break


#save to pandas dataframe

df = pd.DataFrame()

df["primary_keys"] = primary_keys
df["property_types"] = property_types
df["prices"] = prices
df["zipcodes"] = zipcodes
df["street_names"] = street_names
df["localities"] = localities
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

#save to SQL

def pysqldf(q):
    """this function eliminates the need to include locals/globals all the time"""
    return sqldf(q, globals())

conn = sqlite3.connect('web_scrapping.db')
c = conn.cursor()
web_scrapping = pd.read_csv('./web_scrapping.csv')

pysqldf(''' select * from web_scrapping; ''').to_sql('web_scrap', con=conn, index=False, if_exists='append')
conn.commit() 

print('complete')
c.execute('''SELECT * FROM web_scrap''')
results = c.fetchall()
print(results)

#set the schedule

nowtime = str(datetime.datetime.now())

def job(t):
    print("Code is running...", str(datetime.datetime.now()), t)

for time_schedule in ["06:00", "18:00"]:
    schedule.every().monday.at(time_schedule).do(job, time_schedule)
    schedule.every().tuesday.at(time_schedule).do(job, time_schedule)
    schedule.every().wednesday.at(time_schedule).do(job, time_schedule)
    schedule.every().thursday.at(time_schedule).do(job, time_schedule)
    schedule.every().friday.at(time_schedule).do(job, time_schedule)

while True:
    schedule.run_pending()
    time.sleep(30)

