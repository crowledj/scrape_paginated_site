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
                                        StaleElementReferenceException)
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

#https://www.local.ch/fr/q/Vaud%20(Canton)/%20?filter%5Bcategory%5D%5B%5D=25&filter%5Bentry_type%5D=&rid=M5dt

# &filter%5Bcategory%5D%5B%5D=1525&filter%5Bcategory%5D%5B%5D=2080&

#local_ch_link  = 'https://www.local.ch/fr/q?rid=833G&what=+&where=Vaud+%28Canton%29&filter%5Bentry_type%5D=business&filter%5Bcategory%5D%5B%5D=1512&filter%5Bcategory%5D%5B%5D=25&filter%5Bcategory%5D%5B%5D=1114&filter%5Bcategory%5D%5B%5D=1212&filter%5Bcategory%5D%5B%5D=806&filter%5Bcategory%5D%5B%5D=2080&filter%5Bcategory%5D%5B%5D=1382&filter%5Bcategory%5D%5B%5D=1377&filter%5Bcategory%5D%5B%5D=1613&filter%5Bcategory%5D%5B%5D=731&filter%5Bcategory%5D%5B%5D=1335&filter%5Bcategory%5D%5B%5D=1525'
## TODO : must generalize this and add file to code bundle
DRIVER_PATH = r'/usr/bin/chromedriver' #the path where you have "chromedriver" file.



all_categoies_list = [#'Café', 'Restaurant',
# 'Médecins',
# 'Coiffure',
# 'Garage',
# 'Bureau d’architecture',
# 'Menuiserie',
# 'Entreprise de peinture',
# 'Agence immobilière',
# 'Pompes funèbres',
# 'Caves, encuvage',
# 'Institut de beauté',
# 'Installations sanitaires',
'Opticien',
'Fenêtres',
'Demenagements',
'Veterinaire',
'Maçonnerie',
'Fitness Center Institut de beauté',
'Construction métallique',
'Agencement de cuisines',
'Aménagement d’intérieurs',
'Location de véhicules',
'Parquet',
'Horlogerie Bijouterie',
'Boulangerie et pâtisserie ',
'Therapie naturelle',
'Association',
'Médecine traditionnelle chinoise',
'Clinique Ophtalmologique ',
'Minibus Taxi',
'Agence de voyages',
'Paysagistes ',
'Droguerie',
'Etablissement medico-social',
'Entreprise de construction',
'Atelier mécanique',
'Fruits et legumes',
'Magasin de sport',
'Ecole de danse',
'Location de tentes',
'Nutrition',
'Marbrerie',
'Pharmacie',
'Revêtements et sols',
'Auto-école',
'Massage de santé et de sport',
'Stores',
'Vitrerie',
'Personal training',
'Électroménager',
'Reparations',
'Reflexologie',
'Boucherie Charcuterie',
'Traiteur',
'Ferblanterie couverture',
'Vélos cycles',
'Electriciens installateurs',
'Ergotherapie ',
'Entreprise de nettoyage',
'Relooking']


options = Options()
options.headless = True
#options.LogLevel = False
#
# options.add_argument("--window-size=1920,1200")
#options.add_argument("--LogLevel=0")
#options.add_argument("user-agent= 'Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41' ")
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_6) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.698.0 Safari/534.24'")
driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH ) #, service_args=["--verbose", "--log-path=D:\\qc1.log"])
    

# df = pd.DataFrame([('VALAIS Strip club', 'Entertainment', 'www.valaisstrip.com','+336476541128')],
#           columns=('Name','Category', 'Website', 'Phone no.')
#                 )

csvfile = open('category_wise_Swiss_companies_list_oldCodeVAud_rEDO_postfullValaisDone.csv','a', newline='')
header = ('Name', 'Category', 'Website', 'Phone no.')
obj=csv.writer(csvfile)
obj.writerow(header)
#obj.close()
def write_2_csv(name_info='some_shit_company',category='Other', contact_info_TEL='+336471234567', contact_info_webtite='http://www.garbage.com'):

    global csvfile, obj

    
    obj.writerow( (name_info,category, contact_info_TEL, contact_info_webtite) )

    #global df
    # ['DetailEntryName']
    #df.append( (name_info,category, contact_info_TEL, contact_info_webtite ) )


    return True


category_nums= [ '2080','1212','1512','806', '25', '1335','1525','1377', '806', '1114']

num_valais_businesses = 4402
num_businesses_per_page = 10
 
#driver.get(local_ch_link)
business_counter = 0
errors_caught = 0
page_counter = 1

local_ch_link_orig = 'https://www.local.ch/fr/q/Valais%20(Canton)/%20?filter%5Bcategory%5D%5B%5D=1212&filter%5Bentry_type%5D=&rid=M5dt'

#while( business_counter < num_valais_businesses ):
for category_num in category_nums:
    business_counter = 0
    page_counter = 1
    print('Doing category = ' + category_num + ' now ...')

    local_ch_link_updated = local_ch_link_orig.split('Bcategory%5D%5B%5D=')[0] + 'Bcategory%5D%5B%5D=' + str(category_num) + '&filter%5Bentry_type%5D=&rid=M5dt'

    driver.get(local_ch_link_updated)

    time.sleep(1)   

    try:
        source1 = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[1]/div[1]')
    except NoSuchElementException:
        pass

    source1_nah =  False

    try:
        num_valais_businesses_element_text = source1.find_element_by_class_name('search-header-results-title').text
    except NoSuchElementException:
        source1_nah = True
        pass   

    if source1_nah: # and source2 :
        try:
            source2 = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div[1]/div[1]')
            num_valais_businesses_element_text = source2.find_element_by_class_name('search-header-results-title').text
            source1_nah = False
        except NoSuchElementException:
            num_valais_business_vcategory = 500
            pass                

    #num_valais_businesses_element = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[1]/div[1]/div/div/div[1]/div[1]/div/div/h1').text
    print('num_valais_businesses_element = ' + str(num_valais_businesses_element_text))

    num_valais_business_vcategory = int( num_valais_businesses_element_text.split(' ')[0])

    while( business_counter < num_valais_business_vcategory or page_counter > 101 ):
                              
        centra_page_elements = driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[1]/div')
        centra_page_elements_retry = driver.find_elements_by_xpath('/html/body/div[2]/div[1]/div[1]/div')

        if len(centra_page_elements) <= 1:

            centra_page_elements = centra_page_elements_retry

        for index, shop in enumerate(centra_page_elements):
            
            #print('shop no. = ' + str(index))
            #index = len(centra_page_elements) - 1   
            if index == 0 and len(centra_page_elements) != 1:
                continue

            # elif index == len(centra_page_elements) - 1:
            #     break

            elif index == 0 and len(centra_page_elements) == 1:

                # common_link = pagination_link.split('page=')[0] + 'page=' + str(page_counter) + '&rid=833G'  
                # driver.get(common_link)

                page_counter += 1

                common_link = pagination_link.split('page=')[0] + 'page=' + str(page_counter) + '&rid=833G'  
                driver.get(common_link)

                break

            
            elif index == len(centra_page_elements) - 1:
                try:
                    #pagination_display_num = (page_counter + 1) % 4
                    pagination_display_num = page_counter
                    # print('pagination_display_num  = ' + str(pagination_display_num))
                    # #xpath_find_str = './/div/ul/li[' + str(pagination_display_num) + ']/a'
                    xpath_find_str = './/div/ul/li'

                    lis = shop.find_elements_by_xpath(xpath_find_str)

                    for li in lis:
                        try:
                            li_text = li.find_element_by_xpath('.//a').text
                        except:
                            print('no li text')   
                            continue 
                        if li_text == str(page_counter + 1):


                            pagination_link = li.find_element_by_xpath('.//a').get_attribute('href')

                    #pagination_link = shop.find_element_by_xpath(xpath_find_str).get_attribute('href')

                    # if business_counter < 25:
                    #     orig_pagination_link = pagination_link
                        
                    # if not pagination_link:
                    #     pagination_link = orig_pagination_link
                    #     #retry_pagination_link = shop.find_element_by_class_name('pagination-link') #.click()
                    #     #move_page = WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.CLASS_NAME,"pagination-link")))
                    #     get_next_page_link = driver.get(pagination_link)
                    #     print(' pagination_link = ' + str(pagination_link))
                    #     time.sleep(1)                                         
                    #     #driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[1]/div')
                    #     page_counter += 1
                    #     time.sleep(1)
                    # else:

                    # if page_counter == 17:
                    #       page_counter = 18

                    page_counter += 1

                    common_link = pagination_link.split('page=')[0] + 'page=' + str(page_counter) + '&rid=833G'  
                    driver.close()

                    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH ) 
                    driver.get(common_link) 

                    print(' pagination_link = ' + str(common_link))
                    #time.sleep(1)
                    #driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[1]/div')                      
                    
                    #time.sleep(1) 

                except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
                    print("Error caught in the final elif block   :( .....")
                    business_counter += 11
                    errors_caught += 1
                    continue
            else:

                strTimer = time.time()
                company_name_address_etc_info = shop.text.split('\n')  
                
            ## NB !!    ## NOte : this a - element list's final element should have the company's website in it's href !! 

                try:
                    company_name   = company_name_address_etc_info[0]
                    category = company_name_address_etc_info[2] 
                except:
                        print("Error caught in attempt to grab or go to pagination link  0 :( .....")
                        business_counter += 1
                        errors_caught += 1
                        continue                   
                if 'www' in shop.text.lower():
                    try:
                        company_tel_no = company_name_address_etc_info[-1].split('www.')[0]
                        website_name = company_name_address_etc_info[-1].split('www.')[1]
                    except:
                        print("Error caught in attempt to grab or go to pagination link  1 :( .....")
                        business_counter += 1
                        errors_caught += 1
                        continue                        

                elif 'site internet' in shop.text.lower():
                    try:
                        company_phone_email_etc_info_list = shop.find_elements_by_xpath('.//div/div[2]/div[2]/a')
                        company_tel_no = company_phone_email_etc_info_list[2].get_attribute('href') 
                        website_name   = company_phone_email_etc_info_list[-1].get_attribute('href')
                    except:
                        print("Error caught in attempt to grab or go to pagination link  2 :( .....")
                        business_counter += 1
                        errors_caught += 1
                        continue                        

                else:
                    try:
                        company_tel_no = company_name_address_etc_info[-2]
                        website_name   = 'N/A' #company_phone_email_etc_info[-1].get_attribute('href')
                        website_name   = 'N/Acc' #company_phone_email_etc_info[-1].get_attribute('href')
                    except:
                        print("Error caught in attempt to grab or go to pagination link  3 :( .....")
                        business_counter += 1
                        errors_caught += 1
                        continue 

                endTimer = time.time()
                print('Time in main else loop of scraping n pagination stuff = ', str(endTimer - strTimer))    

                #company_phone_email_etc_info = shop.find_element_by_xpath('.//div/div[2]/div[2]/a')  

                #company_website = company_phone_email_etc_info[-1].get_attribute('href')

                contcat_info_links = []
                # for a_sub_elements in company_phone_email_etc_info:
                #     contact_datas = a_sub_elements.get_attribute('href')
                #     contcat_info_links.append(contact_datas)

                print('writing to .csv file --  business_counter = ' + str(business_counter) + ' -- errors_caught = ' + str(errors_caught))
                strtimerCsvWriting = time.time()
                write_2_csv(company_name, category, company_tel_no, website_name)

                endTimerCsvWriting = time.time()
                print('Time in csv writing.. = ', str(endTimerCsvWriting - strtimerCsvWriting)) 

        business_counter += num_businesses_per_page

    csvfile.close()
    csvfile = open('category_wise_Swiss_companies_list_oldCodeVALAIS_redoshostOutputErr_1.csv','a', newline='')

    obj=csv.writer(csvfile)

    obj.writerow( ('next0-cat','next0-cat', 'next0-cat', 'next0-cat') )

        


    #     centra_page_elements = driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[1]/div')
    #     for index, shop in enumerate(centra_page_elements):

    #         print('shop no. = ' + str(index))   
    #         if index == 0:
    #             continue

    #         elif index == len(centra_page_elements) - 1:
    #             try:
    #                 pagination_link = centra_page_elements.find_element_by_xpath('.//div/ul/li/a').get_attribute('href')
    #                 if not pagination_link:
    #                     retry_pagination_link = centra_page_elements.find_element_by_class_name('pagination-link').click()
    #                     time.sleep(3)
    #                 else:
    #                     driver.get(pagination_link)   
    #                     time.sleep(2) 

    #             except (StaleElementReferenceException, NoSuchElementException, InvalidSessionIdException) :
    #                 print("Error caught in attempt to grab or go to pagination link  :( .....")
    #                 business_counter += 1
    #                 continue
    #         else:

    # #/html/body/div[2]/div[2]/div[1]/div[11]/div/div/div[1]/div[1]/a
    # #/html/body/div[2]/div[2]/div[1]/div[2]/div/div/div[1]/div[1]/a
    #             company_name_address_etc_info = shop.find_element_by_xpath('.//div/div/div/div/a').get_attribute('data-gtm-json') 

    #             company_phone_email_etc_info = shop.find_element_by_xpath('.//div/div[2]/div[2]/a')  #.get_attribute('data-gtm-json')   

    #             contcat_info_links = []
    #             for a_sub_elements in company_phone_email_etc_info:
    #                 contact_datas = a_sub_elements.get_attribute('href')
    #                 contcat_info_links.append(contact_datas)


    #             #write_2_csv(contact_datas, contcat_info_links)

    #     business_counter += 1

    
    
