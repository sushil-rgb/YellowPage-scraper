import asyncio
import time
from scrapers.yp_scraper import all_business_urls, scrapeMe, scrapeBusiness


if __name__ == "__main__":
    start_time = time.time()
    
    async def main():
        # make_headless = True
        
        url = input("Enter a searched business category url: ")
        # Example url below:
        # url = https://www.yellowpages.com/search?search_terms=Barbers&geo_location_terms=Moreno+Valley%2C+CA
        # time_interval = 4
        print("Scraping Business urls. Please wait..")
        bizz_urls = await all_business_urls(url)
        print("Scraping datas.")
        scrape_datas = await scrapeMe(bizz_urls)        
        return scrape_datas

    print(asyncio.run(main()))

    total_time = round(time.time()-start_time, 2)
    time_in_secs = round(total_time)
    time_in_mins = round(total_time/60)

    print(f"Took {time_in_secs} seconds | {time_in_mins} minutes.")

