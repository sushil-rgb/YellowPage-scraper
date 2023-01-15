import re
import sys
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup


# random time interval between each requests made to server:
def randomTime():
    ranges = [i for i in range(3, 8)]
    return random.choice(ranges)


# Hundreds of thousands of user agents for server:
def userAgents():
    with open('user-agents.txt') as f:
        agents = f.read().split("\n")
        return random.choice(agents)


def yellowPages(play, heads): # play parameter is for playwright | heads parameter is for switching a browser headless.
    business_links, business_names, business_phones, business_emails, business_street_addresses, business_localities, business_reviews, business_review_counts, business_websites, business_images  = ([] for _ in range(10))
    
    browser = play.chromium.launch(headless=heads, slow_mo=1*1000)
    page = browser.new_page(user_agent=userAgents())

    page.goto('https://www.yellowpages.com/')       
    print(f"Initiating the YellowPage automation | Powered by Playwright.")
    
    try:
        page.wait_for_selector("//input[@id='query']", timeout=30*1000)
    except Exception as e:
        print(f"Content loading error. Please try again in few minutes.")
        sys.exit()

    
    user_input = input("What are you lookin for:> ")
    user_input_ii = input("Enter a location: ")
    print(f"------------------------------\n*Note you can put any number of pages. The script will exit if there are no more pages to scrape.")
    user_input_iii = int(input("Enter a number of pages to scrape:> "))
    
    try:
        page.query_selector("//input[@id='query']").click()
        print(f"Searching......")
        page.keyboard.type(user_input)

        page.wait_for_timeout(timeout=randomTime()*1000)

        page.query_selector("//input[@id='location']").click()        
        page.keyboard.press('Control+A')
        page.keyboard.type(user_input_ii)
    except Exception as e:
        print(f"Content loading error. Please try again in few minutes. Error details |> {e}")
        sys.exit()
        
    page.query_selector("//button[@type='submit']").click()    
    current_url = page.url

    page.goto(current_url)

    main_content = "//div[@class='v-card']"    
    
    try:
        search_words = page.query_selector("//div[@class='search-term']/h1").inner_text().strip()
    except AttributeError:
        pass
    next_button = "//a[@class='next ajax-page']"

    # If the search_words contains 'No results' then script will exit. I approach this step if user type a gibberish word or the search word doesn't exist.
    try:
        pattern = re.search("^No results found for.*", search_words)
    except UnboundLocalError:
        print(f"Invalid location. Please try again in few minutes.")
        sys.exit()
    if pattern != None:
        print(search_words)
        sys.exit()

    # This looop is for pagination of the web page. * Note you can infinite number of pages but the loop will break if there are no more pages.
    for pageNum in range(1, user_input_iii+1):
        print(f"Scraping page | {pageNum}")

        try:
            page.wait_for_selector(main_content, timeout = 30*1000)
        except Exception as e:
            print(f"Contents loading error at page {pageNum}. Scraper has scraped {pageNum-1} pages.")
            break

        business_results = page.query_selector_all(main_content)
        page.wait_for_timeout(timeout = randomTime()*1000)        
        
        for results in business_results:
            try:
                name = results.query_selector("//a[@class='business-name']").inner_text().strip()
            except AttributeError:
                name = "Not available"
            business_names.append(name)

            try:
                hyperlink = f"""https://www.yellowpages.com{results.query_selector("//a[@class='business-name']").get_attribute('href')}"""                  
            except AttributeError:
                hyperlink = "Not available"
            business_links.append(hyperlink)
        
            try:
                contact = results.query_selector("//div[@class='phones phone primary']").inner_text().strip()
            except AttributeError:
                contact = "Not available"
            business_phones.append(contact)
    
            try:
                address = results.query_selector("//div[@class='street-address']").inner_text().strip()
            except AttributeError:
                address = "Not available"
            business_street_addresses.append(address)

            try:
                locality = results.query_selector("//div[@class='locality']").inner_text().strip()
            except AttributeError:
                locality = "Not available"
            business_localities.append(locality)

            try:                
                review = f"""{results.query_selector("//a[@class='rating']/div").get_attribute('class').strip().replace("result-rating ", "")} out of five."""
            except AttributeError:
                review = "Not available"            
            business_reviews.append(review)
            
            try:
                review_count = re.sub(r"[()]", "", results.query_selector("//a[@class='rating']/span").inner_text().strip())
            except AttributeError:
                review_count = "Not available"
            business_review_counts.append(review_count)

            try:
                website = results.query_selector("//a[@class='track-visit-website']").get_attribute('href')
            except AttributeError:
                website = "Not available"
            business_websites.append(website)

            try:
                images = results.query_selector("//div[@class='media-thumbnail']/a/img").get_attribute('src')
                if not images.startswith('https'):
                    images = f"""https:{results.query_selector("//div[@class='media-thumbnail']/a/img").get_attribute('src')}"""                

            except AttributeError:
                images = "Not available."
            business_images.append(images)

        try:
            page.wait_for_selector(next_button, timeout=10*1000)
            page.query_selector(next_button).click()
        except Exception as e:
            print(f"End of the page. The script is exiting.")
            break     

    browser.close()

    print(f"Scraping potential email leads. There are {len(business_links)} businesses. Please wait..")
    for links in range(len(business_links)):        
        print(f"Scraping business number {links+1}|")
        try:
            req = requests.get(business_links[links], headers={'User-Agent': userAgents()})
        except requests.exceptions.ChunkedEncodingError:
            print(f"Oops! Connection error. Scraper is exiting.")
            break        
        soup = BeautifulSoup(req.content, 'lxml')

        try:
            emails = soup.find('a', class_='email-business').get('href').replace("mailto:", "")
        except AttributeError:
            emails = "Not available"
        business_emails.append(emails)


    d = {
        "Business": business_names,
        "Contact": business_phones,
        "Email": business_emails,
        "Street": business_street_addresses,
        "Locality": business_localities,
        "Review": business_reviews,
        "Review count": business_review_counts,
        "Link": business_links,
        "Images": business_images,
        "Website": business_websites,
    }

    df = pd.DataFrame(data=d)
    df.to_excel(f"{search_words}-YellowPage Database.xlsx", index=False)
    print(f"{search_words} database is saved")   
  
                    