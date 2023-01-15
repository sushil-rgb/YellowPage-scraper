from tools import yellowPages
from playwright.sync_api import sync_playwright
import time


start_time = time.time()

make_headless = True


def yellow():
    with sync_playwright() as p:        
        data = yellowPages(p, make_headless)
        return data

print(yellow())

total_time = round(time.time()-start_time, 2)
time_in_secs = round(total_time)
time_in_mins = round(total_time/60)

print(f"Took {time_in_secs} seconds | {time_in_mins} minutes.")