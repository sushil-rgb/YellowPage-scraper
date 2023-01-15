# YellowPage-scraper

<p align='center'>
  <a href = 'https://www.yellowpages.com' target='_blank'><img src='https://en.wikirug.org/images/b/bc/Logo_Yellow_Pages.png'></a>
  </p>

Welcome to the Yellowpage Webscraper using Python Playwright!
This repository contains the code for a web scraper that can extract information from yellow pages websites. The scraper uses the Python Playwright library to automate the process of browsing and extracting data from the website.
To get started, you will need to have Python and and the necessary requirements installed on your machine. You can install Playwright by running the following command:

```python
pip install -r requirements.txt
playwright install
```

The repository includes the following files:

**scraper.py**: This is the main script that initiate the automation.
**tools.py**: This file contains the main code for the scrapera.
**output.xlsx**: This file will be created by the script and will contain the extracted data in xlsx format.

To run the script, simply navigate to the repository directory and run the following command:
```python
python scraper.py
```

The script will then start extracting data from the website based on the configuration settings and will save the data to the output.xlsx file.

Please note that the script is designed to work with yellow pages websites and may not work with other types of websites. Additionally, the script may be blocked by the website if it detects excessive scraping activity, so please use it responsibly.

If you have any issues or suggestions for improvements, please feel free to open an issue on the repository or submit a pull request.

Thank you for using the Yellowpage!
