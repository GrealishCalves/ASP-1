from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
import os
import sqlalchemy

Base = sqlalchemy.orm.declarative_base()


class WeatherData(Base):
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer)
    city = Column(String)
    temperature = Column(Float)
    feels_like = Column(Float)
    average = Column(Float)

    # extended_data(Question 3)
    location = Column(String, nullable=True)
    current_time = Column(String, nullable=True)
    latest_report = Column(String, nullable=True)
    visibility = Column(String, nullable=True)
    pressure = Column(String, nullable=True)
    humidity = Column(String, nullable=True)
    dew_point = Column(String, nullable=True)


class DatabaseHelper:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.session = self.db_config.create_session()
        Base.metadata.create_all(self.db_config.get_engine())

    def insert_or_update_weather_data(self, city_id, city, temperature, feels_like, average=None):
        existing_data = self.session.query(WeatherData).filter(
            WeatherData.city_id == city_id).first()
        if existing_data:
            existing_data.city = city
            existing_data.temperature = temperature
            existing_data.feels_like = feels_like
            existing_data.average = average
            print(f"Data for city with city_id {city_id} updated.")
        else:
            weather_data = WeatherData(
                city_id=city_id, city=city, temperature=temperature, feels_like=feels_like, average=average)
            self.session.add(weather_data)
            print(f"Data for city with city_id {city_id} inserted.")
        self.session.commit()

    def insert_extended_data(self, city_id, extended_data):
        existing_data = self.get_by_city_id(city_id)
        if not existing_data:
            print(f"No existing data found for city with city_id {city_id}.")
            return

        if not extended_data:
            print(
                f"No extended data provided for city with city_id {city_id}.")
            return

        self.update_existing_data(existing_data, extended_data)
        print(f"Extended data for city with city_id {city_id} updated.")
        self.session.commit()

    def update_existing_data(self, existing_data, extended_data):
        attribute_map = {
            'Location': 'location',
            'Current Time': 'current_time',
            'Latest Report': 'latest_report',
            'Visibility': 'visibility',
            'Pressure': 'pressure',
            'Humidity': 'humidity',
            'Dew Point': 'dew_point',
        }
        for key, value in extended_data.items():
            attr_name = attribute_map.get(key)
            if attr_name:
                setattr(existing_data, attr_name, value)
            else:
                print(f"Ignoring unknown key: {key}")

    def get_by_city_id(self, city_id):
        return self.session.query(WeatherData).filter(WeatherData.city_id == city_id).first()

    def get_by_city_name(self, city):
        return self.session.query(WeatherData).filter(WeatherData.city == city).first()


class DatabaseConfig:
    def __init__(self, db_name="data.db"):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(root_dir, db_name)

    def get_engine(self):
        return create_engine(f'sqlite:///{self.db_path}')

    def create_session(self):
        engine = self.get_engine()
        Session = sessionmaker(bind=engine)
        return Session()
