import time
from tools import yellowPages, scrapeMe


start_time = time.time()

make_headless = True

input_phase = yellowPages(make_headless)
extraction_phase = scrapeMe(input_phase)

print(extraction_phase)

total_time = round(time.time()-start_time, 2)
time_in_secs = round(total_time)
time_in_mins = round(total_time/60)

print(f"Took {time_in_secs} seconds | {time_in_mins} minutes.")

