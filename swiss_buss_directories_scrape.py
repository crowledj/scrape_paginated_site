#from scraper_api import ScraperAPIClient
import datetime
import itertools
## turn down level of v verbose by dwfauklt selenium webdriver logging , lol
import logging
import os
import pprint
import random
import re
import smtplib
import subprocess
import sys
import time
#strtime_file = time.time()
import timeit
from collections import defaultdict
from datetime import date
from smtplib import SMTPException

import requests
import selenium

import unidecode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (InvalidSessionIdException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        NoSuchAttributeException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

import csv #pandas as pd
 
#from googletrans import Translator
# init the Google API translator
#translator = Translator()

LOGGER.setLevel(logging.WARNING)

local_ch_link  = 'https://www.local.ch/fr/q?rid=833G&what=+&where=Vaud+%28Canton%29&filter%5Bentry_type%5D=business&filter%5Bcategory%5D%5B%5D=1512&filter%5Bcategory%5D%5B%5D=25&filter%5Bcategory%5D%5B%5D=1114&filter%5Bcategory%5D%5B%5D=1212&filter%5Bcategory%5D%5B%5D=806&filter%5Bcategory%5D%5B%5D=2080&filter%5Bcategory%5D%5B%5D=1382&filter%5Bcategory%5D%5B%5D=1377&filter%5Bcategory%5D%5B%5D=1613&filter%5Bcategory%5D%5B%5D=731&filter%5Bcategory%5D%5B%5D=1335&filter%5Bcategory%5D%5B%5D=1525'
## TODO : must generalize this and add file to code bundle
DRIVER_PATH = r'/usr/bin/chromedriver' #the path where you have "chromedriver" file.

all_categoies_list = ['Café', 'Restaurant',
'Médecins','Coiffure','Garage','Bureau d’architecture',
'Menuiserie','Entreprise de peinture','Agence immobilière',
'Pompes funèbres','Caves, encuvage',
'Institut de beauté','Installations sanitaires',
'Opticien','Fenêtres',
'Demenagements','Veterinaire','Maçonnerie','Fitness Center Institut de beauté',
'Construction métallique','Agencement de cuisines',
'Aménagement d’intérieurs','Location de véhicules','Parquet','Horlogerie Bijouterie',
'Boulangerie et pâtisserie ',
'Therapie naturelle','Association','Médecine traditionnelle chinoise',
'Clinique Ophtalmologique ','Minibus Taxi','Agence de voyages','Paysagistes ','Droguerie',
'Etablissement medico-social','Entreprise de construction',
'Atelier mécanique','Fruits et legumes','Magasin de sport','Ecole de danse',
'Location de tentes',
'Nutrition','Marbrerie','Pharmacie','Revêtements et sols','Auto-école',
'Massage de santé et de sport',
'Stores','Vitrerie','Personal training',
'Électroménager','Reparations','Reflexologie',
'Boucherie Charcuterie','Traiteur','Ferblanterie couverture','Vélos cycles',
'Electriciens installateurs','Ergotherapie ','Entreprise de nettoyage','Relooking']


options = Options()
options.headless = True
#options.LogLevel = False
#
# options.add_argument("--window-size=1920,1200")
#options.add_argument("--LogLevel=0")
#options.add_argument("user-agent= 'Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41' ")
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24'")
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH ) #, service_args=["--verbose", "--log-path=D:\\qc1.log"])
    

csvfile = open('vaudPart_Swiss_companies_list.csv','w', newline='')
header = ('Name', 'Category', 'Website', 'Phone no.')
obj=csv.writer(csvfile)
obj.writerow(header)

csvfile.close()
#obj.close()

def write_2_csv(name_info='some_shit_company',category='Other', contact_info_TEL='+336471234567', contact_info_webtite='http://www.garbage.com'):

    global csvfile, obj
    csvfile = open('vaudPart_Swiss_companies_list.csv','a', newline='')
    obj=csv.writer(csvfile)
    obj.writerow( (name_info,category, contact_info_TEL, contact_info_webtite) )
    csvfile.close()

    return True


num_valais_businesses = 4402
num_businesses_per_page = 11

driver.get(local_ch_link)
business_counter = 0
errors_caught = 0
page_counter = 1
while( business_counter < num_valais_businesses ):

    centra_page_elements = driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[1]/div')

    if not centra_page_elements:
        while not centra_page_elements:

            common_link = pagination_link.split('page=')[0] + 'page=' + str(page_counter +1) + '&rid=833G'  

            print('in infinite while until pagelements found -- page_counter = ' + str(page_counter) + ' -- trying newlyformed common link...')

            # driver.close()
            # driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH ) 

            #strtcloseopenDriverTimer = time.time()
            driver.get(common_link)
            time.sleep(1)
            centra_page_elements = driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[1]/div')

    for index, shop in enumerate(centra_page_elements):
        
        #print('shop no. = ' + str(index))
        #index = len(centra_page_elements) - 1   
        if index == 0 and len(centra_page_elements) == 1:

            # common_link = pagination_link.split('page=')[0] + 'page=' + str(page_counter) + '&rid=833G'  
            # driver.get(common_link)

            # page_counter += 1

            break
            #continue

        elif index == 0 and len(centra_page_elements) != 1:
            continue
        
        elif index == len(centra_page_elements) - 1:
            try:

                #strtFinalBlockTimer = time.time()
                
                #pagination_display_num = (page_counter + 1) % 4
                pagination_display_num = page_counter
                # print('pagination_display_num  = ' + str(pagination_display_num))
                # #xpath_find_str = './/div/ul/li[' + str(pagination_display_num) + ']/a'
                xpath_find_str = './/div/ul/li[2]/a'
                pagination_link = shop.find_element_by_xpath(xpath_find_str).get_attribute('href')

                # if business_counter < 25:0  
                #     orig_pagination_link = pagination_link
                    
                # if not pagination_link:
                #     pagination_link = orig_pagination_link

                if page_counter == 4:
                      page_counter = 4

                common_link = pagination_link.split('page=')[0] + 'page=' + str(page_counter) + '&rid=833G'  

                # driver.close()
                # driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH ) 

                #strtcloseopenDriverTimer = time.time()
                driver.get(common_link)

                #endcloseopenDriverTimer = time.time()
                #print('Time in get Driver call = ', str(endcloseopenDriverTimer - strtcloseopenDriverTimer))                 

                #print(' pagination_link = ' + str(common_link))
                #time.sleep(1)
                #driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[1]/div')                      
                page_counter += 1
                #time.sleep(1) 
                #endFinalBlockTimer = time.time()
                #print('Time in main FinalBlock = ', str(endFinalBlockTimer - strtFinalBlockTimer))    

                if page_counter == 23 or page_counter == 24:
                    check = 1


            except (NoSuchAttributeException, KeyError, IndexError, StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                print("Error caught in the final elif block   :( .....")
                business_counter += 11
                errors_caught += 1
                continue
        else:

            #strTimer = time.time()
            company_name_address_etc_info = shop.text.split('\n')  
            
        ## NB !!    ## NOte : this a - element list's final element should have the company's website in it's href !! 

            try:
                if len(company_name_address_etc_info) >= 3:
                    company_name   = company_name_address_etc_info[0]
                    category = company_name_address_etc_info[2] 
                elif len(company_name_address_etc_info) < 3:    
                    company_name   = company_name_address_etc_info[0]
                    category = 'N/A'
                else:    
                    company_name   = 'N/A'
                    category = 'N/A'
            except (NoSuchAttributeException, KeyError, IndexError, StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException)  :
                    print("Error caught in attempt to grab or go to pagination link  0 :( .....")
                    business_counter += 1
                    errors_caught += 1
                    write_2_csv(company_name, category, company_tel_no, website_name)
                    continue                   
            if 'www' in shop.text.lower():
                try:
                    company_tel_no = company_name_address_etc_info[-1].split('www.')[0]
                    website_name = company_name_address_etc_info[-1].split('www.')[1]
                except:
                    print("Error caught in attempt to grab or go to pagination link  1 :( .....")
                    business_counter += 1
                    errors_caught += 1
                    write_2_csv(company_name, category, company_tel_no, website_name)
                    continue                        

            elif 'site internet' in shop.text.lower():
                try:
                    company_phone_email_etc_info_list = shop.find_elements_by_xpath('.//div/div[2]/div[2]/a')
                    if len(company_phone_email_etc_info_list) >= 3:
                        
                        company_tel_no = company_phone_email_etc_info_list[2].get_attribute('href') 
                        try:
                            website_name   = company_phone_email_etc_info_list[-1].get_attribute('href')
                        except (NoSuchAttributeException, KeyError, IndexError, StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException)  :
                            print("Error caught in attempt to grab website name in 'site internet' block  in the 'pagination link2' block( .....")
                            business_counter += 1
                            errors_caught += 1
                            website_name = 'N/A'
                            write_2_csv(company_name, category, company_tel_no, website_name) 
                            continue                             

                    elif len(company_phone_email_etc_info_list) == 1 or  len(company_phone_email_etc_info_list) == 2 :
                        website_name = company_phone_email_etc_info_list[-1].get_attribute('href') 
                        company_tel_no   = 'N/A'
                    else:
                        company_tel_no = 'N/A'
                        website_name = 'N/A'                           
                except (NoSuchAttributeException, KeyError, IndexError, StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                    print("Error caught in attempt to grab or go to pagination link  2 :( .....")
                    business_counter += 1
                    errors_caught += 1
                    write_2_csv(company_name, category, company_tel_no, website_name)
                    continue                        

            else:
                try:
                    if len(company_name_address_etc_info) >= 2:
                        company_tel_no = company_name_address_etc_info[-2]
                    elif len(company_name_address_etc_info) == 1:
                        company_tel_no = company_name_address_etc_info[-1]
                    else:
                        company_tel_no = 'N/A'    
                except (NoSuchAttributeException, KeyError, IndexError, StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                    print("Error caught in attempt to grab or go to pagination link  3 :( .....")
                    business_counter += 1
                    errors_caught += 1
                    write_2_csv(company_name, category, company_tel_no, website_name)
                    continue 

            #endTimer = time.time()
            #print('Time in main else loop of scraping n pagination stuff = ', str(endTimer - strTimer))    

            #company_phone_email_etc_info = shop.find_element_by_xpath('.//div/div[2]/div[2]/a')  

            #company_website = company_phone_email_etc_info[-1].get_attribute('href')

            contcat_info_links = []
            # for a_sub_elements in company_phone_email_etc_info:
            #     contact_datas = a_sub_elements.get_attribute('href')
            #     contcat_info_links.append(contact_datas)

            #print('writing to .csv file --  business_counter = ' + str(business_counter) + ' -- errors_caught = ' + str(errors_caught))
            #strtimerCsvWriting = time.time()
            write_2_csv(company_name, category, company_tel_no, website_name)

            #endTimerCsvWriting = time.time()
            #print('Time in csv writing.. = ', str(endTimerCsvWriting - strtimerCsvWriting)) 

    business_counter += num_businesses_per_page
    print('Done with page ' + str(page_counter) + ' -- writeen 11 lines  to .csv file --  business_counter = ' + str(business_counter) + ' -- errors_caught = ' + str(errors_caught))
print('finished file !! ')
#csvfile.close()
   
