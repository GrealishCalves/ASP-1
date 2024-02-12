import random
import pytest
from playwright.sync_api import sync_playwright
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DatabaseHelper

RANDOM_CITY = "London"
NUMBER_OF_CITIES_TO_INSERT = 5
PLAYWRIGHT_HEADLESS=True

class WeatherDataHandler:
    country = "Israel"

    def __init__(self, api_helper: ApiHelper, db_helper: DatabaseHelper):
        self.api = api_helper
        self.db = db_helper

    def fetch_data_for_cities(self, country):
        return self.api.get_cities(country)

    def get_city_hash(self, city):
        return self.api.get_city_hash(city)

    def get_hash(self, city):
        city_path = self.get_city_hash(city)
        return city, city_path

    def get_test(self, city):
        return self.api.get_test(city)

    def get_city_data(self, city):
        return self.api.get_current_weather(city)

    def fetch_random_city(self):
        response = self.fetch_data_for_cities(country=self.country)
        cities = response.get("data", [])
        if cities:
            return random.choice(cities)

    def get_by_city_name(self, city):
        return self.db.get_by_city_name(city)

    def fetch_and_process_city_data(self, weather_handler, city_name):
        city_data_response = weather_handler.get_city_data(city_name)
        if city_data_response.status_code == 200:
            city_data = city_data_response.json()
            processed_data = self.process_city_data(
                weather_handler, city_name, city_data)
            return processed_data
        else:
            print(
                f"Failed to fetch weather data for {city_name}, status code: {city_data_response.status_code}")
            return False

    def process_city_data(self, weather_handler, city_name, city_data):
        city_id = city_data.get('id')
        if city_id is None:
            print(f"City ID not found for {city_name}. Skipping processing.")
            return None

        main_data = city_data.get('main', {})
        temperature, feels_like, temp_min, temp_max = self.extract_temperature_data(
            main_data)

        if None in [temperature, feels_like, temp_min, temp_max]:
            print(
                f"Missing temperature data for {city_name}. Skipping processing.")
            return None

        average = self.calculate_average_temp(temp_min, temp_max)

        self.insert_weather_data(weather_handler, city_id,
                                 city_name, temperature, feels_like, average)
        print(f"Weather data for {city_name} fetched and processed.")
        return {
            "city_name": city_name,
            "city_id": city_id,
            "temperature": temperature,
            "feels_like": feels_like,
            "average": average
        }

    def extract_temperature_data(self, main_data):
        temperature = main_data.get('temp')
        feels_like = main_data.get('feels_like')
        temp_min = main_data.get('temp_min')
        temp_max = main_data.get('temp_max')
        return temperature, feels_like, temp_min, temp_max

    def calculate_average_temp(self, temp_min, temp_max):
        return (temp_min + temp_max) / 2

    def insert_weather_data(self, weather_handler, city_id, city_name, temperature, feels_like, average):
        weather_handler.db.insert_or_update_weather_data(
            city_id, city_name, temperature, feels_like, average)


class Scraper:
    header_city = "null"

    def extract_table_data(self, page):
        rows = page.query_selector_all(
            '.table.table--left.table--inner-borders-rows tbody tr')
        table_data = {}

        for row in rows:
            key_element = row.query_selector('th')
            value_element = row.query_selector('td')

            if key_element and value_element:
                key = key_element.inner_text().strip().rstrip(':')
                value = value_element.inner_text().strip()
                table_data[key] = value
            else:
                print('Invalid row structure - missing key or value')

        return table_data

    def _scrape_weather_data(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=PLAYWRIGHT_HEADLESS, channel="chrome")
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            table_data = self.extract_table_data(page)
            header = page.get_by_role(
                "heading").all_text_contents()
            self.header_city = header[0]
            browser.close()
        return table_data, self.header_city

    def scrape_weather_data_for_city(self, city_path):
        url = f"https://www.timeanddate.com{city_path.lower()}"
        print(url)
        return self._scrape_weather_data(url), self.header_city


@pytest.fixture(scope="class")
def weather_handler(api_helper, db_helper):
    return WeatherDataHandler(api_helper(), db_helper())


@pytest.fixture(scope="class")
def api_helper():
    return ApiHelper


@pytest.fixture(scope="class")
def db_helper():
    return DatabaseHelper


@pytest.fixture(scope="class")
def scraper():
    return Scraper()


@pytest.fixture
def header_city_fixture():
    header_city = None
    yield header_city


class Test:
    def test_case_one(self, weather_handler, n=NUMBER_OF_CITIES_TO_INSERT):
        api_data = {}
        attempts = 0
        max_attempts = n + 5

        while len(api_data) < n and attempts < max_attempts:
            attempts += 1
            city_name = weather_handler.fetch_random_city()
            if not city_name:
                continue

            success = weather_handler.fetch_and_process_city_data(
                weather_handler, city_name)
            if success:
                api_data[city_name] = success

        assert len(
            api_data) == n, f"Expected data for {n} cities but got {len(api_data)}. Attempts made: {attempts}"

    # @pytest.mark.skip(reason="Skipping this test case")
    def test_case_two(self, weather_handler, scraper):
        random_city = RANDOM_CITY
        get_city_path = weather_handler.get_test(random_city)
        scrape_data, header_city = scraper.scrape_weather_data_for_city(
            get_city_path)

        if scrape_data:
            table_data, header_city = scrape_data
            scrape_city_name = table_data["Location"]
            city_name = self.extract_city_name(header_city)
            city_data = weather_handler.get_by_city_name(city_name)
            if city_data:
                self.process_city_data(
                    weather_handler, city_name, city_data, table_data)
            else:
                self.handle_missing_data(scrape_city_name, weather_handler)

    def extract_city_name(self, header_city):
        split_words = header_city.split()
        index_of_in = split_words.index("in")
        city_name = split_words[index_of_in + 1]
        if city_name.endswith(','):
            city_name = city_name[:-1]
        return city_name

    def process_city_data(self, weather_handler, city_name, city_data, table_data):
        city_id = city_data.city_id
        weather_handler.db.insert_extended_data(
            city_id=city_id, extended_data=table_data)

    def handle_missing_data(self, scrape_city_name, weather_handler):
        first_word_location = scrape_city_name.split()[0]
        print(f"No data found for {first_word_location} in the database")
