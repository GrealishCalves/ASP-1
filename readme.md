# Weather API Testing README

### Overview
This document outlines the setup and testing procedures for weather data collection, processing, and storage. It focuses on testing API integration, database integrity, and web scraping functionality using Python, pytest, and Playwright.

### Setup
Ensure the following dependencies are installed to run the tests:
- Python 3.x
- pytest
- Playwright

Install dependencies with pip:
```bash
pip install -r requirements.txt
```

### Execute
from a root DIR:
```bash
 pytest -s ./tests/test_question_XXX.py
``` 

### API and Web Sources
- City Lists API: https://countriesnow.space/api/v0.1/countries/cities
- Weather Data API: https://api.openweathermap.org/data/2.5/weather
- Web Scraping Source: https://www.timeanddate.com


## Question One

**Configuration**

 `DEFAULT_CITY_FOR_TESTS`: city data to fetch

**Test Case One**
- Confirms the weather API is accessible and returns a successful response.

**Test Case Two**
- Verifies that the `temperature`, and `feels_like` data stored in the database exactly match the data fetched from the API.

## Question Two

### Configuration
`WeatherDataHandler.CITIES`: Specifies the list of cities for which to retrieve data.

### Test Case One
- Extracting and recording key metrics (temperature, feels_like, average temperature).
- Calculate Average based on the `(temp_min + temp_max) / 2`
- Confirms database accurately mirrors API data for each city.
- Identifies the city with the highest average temperature.


## Bonus Question

### disclamer
Selenium wasn't part of my usual workflow, Initially considered Selenium, but due to setup difficulties, switched to Playwright for its simplicity and no additional driver requirements, enhancing our scraping capabilities.

### Setup

**Country Cities API**: Retrieves city lists by country.
```
https://countriesnow.space/api/v0.1/countries/cities
```

**Weather Information Source**: 
```
https://www.timeanddate.com
```

**City Weather API**: Fetches weather data by city.
```
https://api.openweathermap.org/data/2.5/weatherz
```

### Configuration
- `RANDOM_CITY` selects a random city for data scraping purposes.
- `WeatherDataHandler.country` specified country.
- `NUMBER_OF_CITIES_TO_INSERT` to determine the number of cities for data insertion.
- `PLAYWRIGHT_HEADLESS` to determine if lunch the browser while scraping [default is not]

### Test Case One
- Retrieve and process weather data for randomly selected cities, ensuring diverse data coverage.
- Randomly selects cities, implementing a retry mechanism for failed API responses.
- Fetches, processes, and stores city weather data.
- Verifies successful data retrieval and storage for a predefined number of cities.

### Test Case Two

- Validates database-stored weather data against data scraped from the web.
- Uses Playwright to extract weather data from `www.timeanddate.com`.
- Matches scraped data with database entries to confirm extend more data.
