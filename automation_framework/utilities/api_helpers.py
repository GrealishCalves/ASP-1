import os
import requests
from configparser import ConfigParser

class ApiHelper:
    def __init__(self):
        root_dir = self.find_root_directory()
        config_file = os.path.join(root_dir, 'automation_framework', 'config', 'config.ini')
        config = ConfigParser()
        config.read(config_file)
        self.BASE_URL = config.get('API', 'base_url')
        self.API_KEY = config.get('API', 'api_key')

    def find_root_directory(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        
        while current_dir != '/':
            if os.path.exists(os.path.join(current_dir, 'automation_framework')):
                return current_dir
            current_dir = os.path.dirname(current_dir)

        raise FileNotFoundError("Root directory containing 'automation_framework' not found.")

    def get_current_weather(self, city):
        url = self.BASE_URL + "?q=" + city + "&appid=" + self.API_KEY
        response = requests.get(url)
        return response

    def get_cities(self, country):
        url = "https://countriesnow.space/api/v0.1/countries/cities"
        body = {
            "country": country
        }
        response = requests.post(url, data=body)
        return response.json()

    def get_test(self, city):
        url = f"https://www.timeanddate.com/scripts/completion.php?query={city}&xd=5&mode=ci"
        response = requests.get(url)
        response_text = response.text
        lines = response_text.split("\n")

        for line in lines:
            if not line.startswith('/'):
                continue  # Skip lines not starting with '/'

            if not line.startswith('/weather/'):
                continue  # Skip lines not starting with '/weather/'

            if "@" in line:
                continue  # Skip lines containing "@"

            value = line.split('\t')[0]
            return value

        return None
