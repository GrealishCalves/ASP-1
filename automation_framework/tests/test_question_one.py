import pytest
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DatabaseHelper

DEFAULT_CITY_FOR_TESTS = "Rome"


@pytest.fixture(scope="class")
def weather_api(api_helper):
    return WeatherAPI(api_helper, DEFAULT_CITY_FOR_TESTS)


@pytest.fixture(scope="class")
def weather_db(db_helper):
    return WeatherDB(db_helper)


@pytest.fixture(scope="class")
def api_helper():
    return ApiHelper()


@pytest.fixture(scope="class")
def db_helper():
    return DatabaseHelper()


@pytest.fixture(scope="class")
def fetched_weather(weather_api):
    response = weather_api.fetch_weather()
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    return response.json()


class WeatherAPI:
    def __init__(self, api_helper: ApiHelper, default_city="Madrid"):
        self.api = api_helper
        self.default_city = default_city

    def fetch_weather(self, city=None):
        city = city or self.default_city
        return self.api.get_current_weather(city)


class WeatherDB:
    def __init__(self, db_helper: DatabaseHelper):
        self.db = db_helper

    def insert_or_update_weather(self, weather_data, city_id):
        temperature = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        self.db.insert_or_update_weather_data(
            city_id, weather_data['name'], temperature, feels_like)

    def assert_weather_data(self, city_id, expected_temperature, expected_feels_like):
        db_data = self.db.get_by_city_id(city_id)
        assert db_data.temperature == expected_temperature, "Temperature verification failed."
        assert db_data.feels_like == expected_feels_like, "Feels_like verification failed."


class TestWeatherAPI:
    def test_case_one(self, weather_db, fetched_weather):
        city_id = fetched_weather['id']
        weather_db.insert_or_update_weather(fetched_weather, city_id)

    def test_case_two(self, weather_db, fetched_weather):
        city_id = fetched_weather['id']
        expected_temperature = fetched_weather['main']['temp']
        expected_feels_like = fetched_weather['main']['feels_like']

        weather_db.assert_weather_data(
            city_id, expected_temperature, expected_feels_like)
