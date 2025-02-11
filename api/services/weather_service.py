import aiohttp
from typing import List
from api.models.geo import GeoPoint
from api.models.weather import Meteorology


class WeatherService:
    _instance = None  # Variable para almacenar la única instancia

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def fetch_meteorology(cls, coords: List[GeoPoint]) -> List[Meteorology]:
        lats = ",".join(str(coord['lat']) for coord in coords)
        longs = ",".join(str(coord['lon']) for coord in coords)

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={longs}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                json = await response.json()
                json = [json] if not isinstance(json, list) else json

                data = [{
                    'humidity': d['current']['relative_humidity_2m'],
                    'velocity': d['current']['wind_speed_10m'],
                    'temperature': d['current']['temperature_2m'],
                    'direction': d['current']['wind_direction_10m']
                } for d in json]

                return data
