import re
import sys
import random
import requests
import pandas as pd
from lxml import etree
from time import sleep
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


# random time interval between each requests made to server:
# You can decrease the time interval for faster scraping however I discourage you to do so as it may hurt the server.
# Scrape responsibly:
def randomTime():
    ranges = [i for i in range(3, 8)]
    return random.choice(ranges)


# Hundreds of thousands of user agents for server:
def userAgents():
    with open('user-agents.txt') as f:
        agents = f.read().split("\n")
        return random.choice(agents)
       
   
def yellowPages(heads): # play parameter is for playwright | heads parameter is for switching a browser headless.       
    with sync_playwright() as play:
        browser = play.chromium.launch(headless=heads, slow_mo=1*1000)
        page = browser.new_page(user_agent=userAgents())

        page.goto('https://www.yellowpages.com')       
        print(f"Initiating the YellowPage automation | Powered by Playwright.")
    
        try:
            page.wait_for_selector("//input[@id='query']", timeout=30*1000)
        except PlaywrightTimeoutError:
            print(f"Content loading error. Please try again in few minutes.")
            sys.exit()
    
        user_input_business = input("What are you lookin for:> ")
        user_input_location = input("Enter a location: ")            
    
        # Business search area:
        page.query_selector("//input[@id='query']").click()
        print(f"Searching. Please wait.....")
        page.keyboard.type(user_input_business)

        page.wait_for_timeout(timeout=randomTime()*1000)

        # Location search area:
        page.query_selector("//input[@id='location']").click()        
        page.keyboard.press('Control+A')
        page.keyboard.type(user_input_location)

        page.query_selector("//button[@type='submit']").click()

        current_url = page.url     
        location = current_url.split("=")[-1].capitalize()   
        pagination = "//div[@class='pagination']/span"
        
        try:
            page.wait_for_selector(pagination, timeout=5*1000)
        except PlaywrightTimeoutError:
            print(f"Content loading error. Please try again in few minutes.")
            sys.exit()

        browser.close()
   
        # 101 is just a random number. The scraper will exist if there are no contents.
        total_page_urls = [f"{current_url}&page={num}" for num in range(1, 101)]
        total_business_urls = []

        # Iterating and using beautifulsoup to extract all business urls:
        for idx, url in enumerate(total_page_urls):        
            sleep(randomTime())
            try:
                req = requests.get(url, headers={'User-Agent': userAgents()})
            except requests.exceptions.ConnectTimeout:
                print(f"Connection error. Skipping url {url}")
                continue        
            
            # Making soup and using LXML for xpath approach:
            soup = etree.HTML(str(BeautifulSoup(req.content, 'lxml')))
            
            global categories
            categories = f"""{''.join(soup.xpath("//div[@class='breadcrumb']/span/text()"))} in {location}."""
            page_content = ''.join(soup.xpath("//div[@class='search-term']/h1/text()"))

            # If the search_words contains 'No results' then script will exit. I approach this step if user type a gibberish word or the search word doesn't exist.
            pattern = re.search("^No results found for.*", page_content)  
            business_links = [f"https://www.yellowpages.com{link}" for link in soup.xpath("//a[@class='business-name']/@href")]
            total_business_urls.extend(business_links)  
            
            if pattern != None: 
                print(f"No content. Please try again in few minutes.")           
                break       
        
        return total_business_urls

    
def scrapeMe(url_lists):
    yellow_in_dicts = []
    print(f"Category | {categories}. Number of business | {len(url_lists)}.")
    for idx, urls in enumerate(url_lists):
        sleep(randomTime())        
        try:
            req = requests.get(urls, headers={'User-Agent': userAgents()})
        except requests.exceptions.ConnectionError:
            print(f"Connection error. Skipping URL ({idx}) | {urls}")
            continue

        soup = etree.HTML(str(BeautifulSoup(req.content, 'lxml')))        
        
        business_names = ''.join(soup.xpath("//h1[@class='dockable business-name']/text()"))        
        print(f"Scraping business | {business_names}")

        datas = {
            "Business": business_names,
            "Contact": ''.join(soup.xpath("//a[@class='phone dockable']/strong/text()")),
            "Email": ''.join(soup.xpath("//a[@class='email-business']/@href")).replace("mailto:", ""),
            "Address": ''.join(soup.xpath("//span[@class='address']/text()")),
            "Map and direction": ''.join(f'''https://www.yellowpages.com{soup.xpath("//a[@class='directions small-btn']/@href")}'''), 
            "Review": ''.join(soup.xpath("//a[@class='yp-ratings']/div/@class")).replace("rating-stars ", ""),
            "Review count": re.sub(r"[()]", "", ''.join(soup.xpath("//a[@class='yp-ratings']/span[@class='count']/text()"))), 
            "Hyperlink": urls,
            "Images": ''.join(soup.xpath("//img[@class='biz-card-thumbnail']/@src")), 
            "Website": ''.join(soup.xpath("//a[@class='website-link dockable']/@href")), 
        }

        yellow_in_dicts.append(datas)
    
    df = pd.DataFrame(yellow_in_dicts)
    df.to_excel(f"{categories}-YellowPage database.xlsx", index=False)
    print(f"Database saved | {categories}.")

