import re
import asyncio
import aiohttp
import requests
import pandas as pd
from lxml import etree
from time import sleep
from bs4 import BeautifulSoup

from tools.functionalities import userAgents, randomTime, verify_yellow, yaml_by_select, yp_lists,create_path
       
   
async def yellowPages(yp_url): # play parameter is for playwright | heads parameter is for switching a browser headless.       
    async with aiohttp.ClientSession() as session:
        # if verify_yellow(yp_url):
        #     return "Invalid link"

        scrape = yaml_by_select('selectors')    

        # 101 is just a random number. The scraper will exist if there are no contents.
        total_page_urls = yp_lists(yp_url)
        total_business_urls = []

        # Iterating and using beautifulsoup to extract all business urls:
        for idx, url in enumerate(total_page_urls):      
            try:                
                async with session.get(url, headers={'User-Agent': userAgents()}) as response:
                    # sleep(randomTime(interval))
                    # Making soup and using LXML for xpath approach:
                    soup = etree.HTML(str(BeautifulSoup(await response.text(), 'lxml')))
                    
                    global categories
                    categories = f"""{''.join(soup.xpath(scrape['categories']))} in ."""
                    page_content = ''.join(soup.xpath(scrape['page_content']))

                    # If the search_words contains 'No results' then script will exit. I approach this step if user type a gibberish word or the search word doesn't exist.
                    pattern = re.search("^No results found for.*", page_content)  
                    business_links = [f"https://www.yellowpages.com{link}" for link in soup.xpath(scrape['business_urls'])]
                    total_business_urls.extend(business_links)
                    
                    if pattern != None: 
                        print(f"No content. Please try again in few minutes.")           
                        break                           
            except (requests.exceptions.ConnectTimeout, aiohttp.ClientError):
                print(f"Connection error. Skipping url {url}")
                break                  
            
        return total_business_urls
    

async def all_business_urls(url):
    boy_task = await asyncio.create_task(yellowPages(url))
    return boy_task

    
async def scrapeBusiness(urls):
    scrape = yaml_by_select('selectors')
    # responses = await all_business_urls(urls)
    yellow_in_dicts = []
    async with aiohttp.ClientSession() as session:        
        async with session.get(urls, headers={'User-Agent': userAgents()}) as response:        
            content = await response.read()
            soup = etree.HTML(str(BeautifulSoup(content, 'lxml')))
            business_names = ''.join(soup.xpath(scrape['business_name']))            
            datas = {
                "Business": business_names,
                "Contact": ''.join(soup.xpath(scrape['contact'])),
                "Email": ''.join(soup.xpath(scrape['email'])).replace("mailto:", ""),
                "Address": ''.join(soup.xpath(scrape['address'])),
                "Map and direction": ''.join(f'''https://www.yellowpages.com{soup.xpath(scrape['map_and_direction'])}'''), 
                "Review": ''.join(soup.xpath(scrape['review'])).replace("rating-stars ", ""),
                "Review count": re.sub(r"[()]", "", ''.join(soup.xpath(scrape['review_count']))), 
                "Hyperlink": urls,
                "Images": ''.join(soup.xpath(scrape['images'])), 
                "Website": ''.join(soup.xpath(scrape['website'])), 
            }
            yellow_in_dicts.append(datas)
        return yellow_in_dicts


async def scrapeMe(url_lists):    
    yellow_in_dicts = []
    print(f"Scraping | {categories}. Number of business | {len(url_lists)}. Please wait.")
    
    tasks = [scrapeBusiness(url) for url in url_lists]    
    results = await asyncio.gather(*tasks)
    for res in results:
        yellow_in_dicts += res

    create_path('Yellowpage database')
    df = pd.DataFrame(yellow_in_dicts)
    df.to_excel(f'Yellowpage database//{categories}.xlsx', index=False)
    print('Scraping complete.')

