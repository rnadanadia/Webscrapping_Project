import pytest
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import pandas as pd
import schedule
import datetime
import time

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


driver = webdriver.Safari()

def get_info(links):
    driver.get(links)
    soup = BeautifulSoup(driver.page_source, "lxml")
    
    #price
    for price_str in soup.find_all('p', {'class':'classified__price'}):
        for price in price_str('span', {'class':'sr-only'}):
            price = re.findall(r'[\d]+', price.text)[0]
            prices.append(price)
            print("Price: ", prices[-1])
        
    #zipcode and locality
    try: 
        locality_str = soup.find_all('span', {'class':'classified__information--address-row'})[1]
        locality_str = " ".join(re.findall(r'[A-Za-z0-9 -]', locality_str.text))
        locality_str= locality_str.replace(" ", "")
        
        locality = (re.findall(r'[A-Za-z]+', locality_str))[0]
        localities.append(locality)
        print('Locality: ', localities[-1])
    except:
        locality_str = soup.find_all('span', {'class':'classified__information--address-row'})[0]
        locality_str = " ".join(re.findall(r'[A-Za-z0-9 -]', locality_str.text))
        locality_str= locality_str.replace(" ", "")
        
        locality = (re.findall(r'[A-Za-z]+', locality_str))[0]
        localities.append(locality)
        print('Locality: ', localities[-1])
    
    zipcode = (re.findall(r'[\d]+', locality_str))[0]
    zipcodes.append(zipcode)
    print('Zipcode: ', zipcodes[-1])
  
  
    #property
    property_info = soup.find('h1', {'class':'classified__title'})
    property = " ".join(re.findall(r'[A-Za-z]+', property_info.text))
    property = property.replace("for sale", "")
    property_types.append(property)
    print("Property type: ", property_types[-1])
    

    #bedrooms
    find_bedrooms = soup.find_all('tr', {'class':'classified-table__row'})
    for bedroom in find_bedrooms:
        if "Bedrooms" in bedroom.text:
            bedroom = re.findall(r'[\d]+', bedroom.text)[0]
            bedrooms.append(bedroom)
            print('Bedroom: ',bedrooms[-1])
    
    #bathrooms
    find_bathroom = soup.find_all('tr', {'class':'classified-table__row'})
    for bathroom in find_bathroom:
        if "Bathrooms" in bathroom .text:
            bathroom = re.findall(r'[\d]+', bathroom.text)[0]
            bathrooms.append(bathroom)
            print('Bathroom: ',bathrooms[-1])
                
                
    #living area
    find_living_area = soup.find_all('tr', {'class':'classified-table__row'})
    for living_area in find_living_area:
        try:
            if "Living area" in living_area.text:
                living_area = re.findall(r'[\d]+', living_area.text)
                living_areas.append(living_area)
                print('Living area size: ',living_areas[-1])
        except:
            if "Living area" not in living_area.text:
                living_areas.append(None)
                print('Living area size: ',living_areas[-1])
                
            
    #equipped kitchen    
    find_equipped_kitchen = soup.find_all('tr', {'class':'classified-table__row'})
    for equipped_kitchen in find_equipped_kitchen:
        try:
            if "Equipped kitchen" in equipped_kitchen.text:
                equipped_kitchen = re.findall(r'[A-Za-z]+', equipped_kitchen.text)[0]
                equipped_kitchens.append(equipped_kitchen)
                print('Equipped kitchen: ',equipped_kitchens[-1])
        except:
            if "Equipped kitchen" not in equipped_kitchen.text:
                equipped_kitchens.append(None)
                print('Equipped kitchen: ',equipped_kitchens[-1])
                
                
    #furnished
    find_furnished = soup.find_all('tr', {'class':'classified-table__row'})
    for furnished in find_furnished:
        try:
            if "Furnished" in furnished.text:
                furnished = re.findall(r'[A-Za-z]+', furnished.text)[0]
                furnisheds.append(furnished)
                print('Furnished: ',furnisheds[-1])
        except:
            if "Furnished" not in furnished.text:
                furnisheds.append(None)
                print('Furnished: ',furnisheds[-1])


    #garden area
    find_garden_surface = soup.find_all('tr', {'class':'classified-table__row'})
    for garden_surface in find_garden_surface:
        try:
            if "Garden surface" in garden_surface.text:
                garden_surface = re.findall(r'[\d]+', garden_surface.text)[0]
                garden_surfaces.append(garden_surface)
                print('Garden surface: ',garden_surfaces[-1])
        except:
            if "Garden surface" not in garden_surface.text:
                garden_surfaces.append(None)
                print('Garden surface: ',garden_surfaces[-1])
    
    
    #surface plot
    find_surface = soup.find_all('tr', {'class':'classified-table__row'})
    for surface in find_surface:
        if "Surface of the plot" in surface.text:
            surface = re.findall(r'[\d]+', surface.text)[0]
            surface_plots.append(surface)
            print('Surface plot: ',surface_plots[-1])
    
    
    #building condition
    find_building_condition = soup.find_all('tr', {'class':'classified-table__row'})
    for building_condition in find_building_condition:
        try:
            if "Building condition" in building_condition.text:
                building_condition = re.findall(r'(A-Za-z)+', building_condition.text)[0]
                building_conditions.append(building_condition)
                print('Building condition: ',building_conditions[-1])
        except:
            if "Building condition" not in building_condition.text:
                building_conditions.append(None)
                print('Building condition: ',building_conditions[-1])
            
                
    #energy class
    find_energy_class = soup.find_all('tr', {'class':'classified-table__row'})
    for energy_class in find_energy_class:
        try:
            if "Energy Class" in energy_class.text:
                energy_class= re.findall(r'(A-Za-z)+', energy_class.text)[0]
                energy_classes.append(energy_class)
                print('Energy_class: ',energy_classes[-1])
        except:
            if "Energy Class" not in energy_class.text:
                energy_classes.append(None)
                print('Energy_class: ',energy_classes[-1])

    df = pd.DataFrame()

 
    df["price"] = prices
    df["zipcodes"] = zipcodes
    df["localities"] = localities
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
    
    df.to_csv("web_scrapping.csv", mode = "w", header=True)

counts = 0
for i in range(1,5):
    url = f'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&page={i}&orderBy=relevance'
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    for pages in soup.find_all('li', {'class':'search-results__item'}):
        for links in pages.find_all('a', {'class':'card__title-link'}):
            counts += 1
            print(f'page number: {i}, click count: {counts}')
            print(links['href'])
            get_info(links["href"])
            


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