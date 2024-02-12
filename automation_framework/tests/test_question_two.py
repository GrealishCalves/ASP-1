import pytest
import sys
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DatabaseHelper


class WeatherDataHandler:
    CITIES = ["Milan", "Paris", "London", "New York", "Tokyo", "Sydney"]

    def __init__(self, api_helper: ApiHelper, db_helper: DatabaseHelper):
        self.api = api_helper
        self.db = db_helper

    def fetch_data_for_cities(self):
        api_data = {}

        for city_name in self.CITIES:
            response = self.api.get_current_weather(city_name)
            if response.status_code == 200:
                data = response.json()
                weather_data = self.extract_weather_data(data)
                self.db.insert_or_update_weather_data(*weather_data)

                api_data[city_name] = {
                    "city_name": city_name,
                    "city_id": weather_data[0],
                    "temperature": weather_data[2],
                    "feels_like": weather_data[3],
                    "average": weather_data[4]
                }
            else:
                print(f"Failed to fetch weather data for {city_name}")

        return api_data

    def extract_weather_data(self, data):
        city_id = data['id']
        temperature = data['main']['temp']
        feels_like = data['main']['feels_like']
        temp_min = data['main']['temp_min']
        temp_max = data['main']['temp_max']
        average = self.calculate_average_temperature(temp_min, temp_max)

        return city_id, data['name'], temperature, feels_like, average

    @staticmethod
    def calculate_average_temperature(temp_min, temp_max):
        return (temp_min + temp_max) / 2


@pytest.fixture(scope="class")
def weather_handler(api_helper, db_helper):
    return WeatherDataHandler(api_helper, db_helper)


@pytest.fixture(scope="class")
def api_helper():
    return ApiHelper()


@pytest.fixture(scope="class")
def db_helper():
    return DatabaseHelper()


class TestWeatherAPI:
    def test_case_one(self, weather_handler):
        api_data = weather_handler.fetch_data_for_cities()
        highest_average_temp_city = self.get_highest_average_temp(
            api_data)
        print(
            f"The city with the highest average temperature is: {highest_average_temp_city}")

        for city, api_info in api_data.items():
            db_data = weather_handler.db.get_by_city_id(api_info["city_id"])

            assert db_data is not None
            assert db_data.city_id == api_info["city_id"]
            assert db_data.temperature == pytest.approx(
                api_info["temperature"])
            assert db_data.feels_like == pytest.approx(api_info["feels_like"])
            assert db_data.average == pytest.approx(api_info["average"])

    def get_highest_average_temp(self, api_data):
        max_average_temp = float('-inf')
        city_with_highest_temp = None
        for city, data in api_data.items():
            if data['average'] > max_average_temp:
                max_average_temp = data['average']
                city_with_highest_temp = city
        return city_with_highest_temp
