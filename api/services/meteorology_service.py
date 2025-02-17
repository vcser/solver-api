from typing import List
from api.models.meteorology import Meteorology
from api.models.data import RequestData
import aiohttp

class MeteorologyService:
    _instance = None  # Variable para almacenar la única instancia

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def fetch_meteorology(cls, coords: RequestData) -> List[Meteorology]:
        lats = ",".join(str(fire.lat) for fire in coords.fires)
        longs = ",".join(str(fire.lon) for fire in coords.fires)

        url = f"https://api.open-meteo.com/v1/forecast?latitude={lats}&longitude={longs}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                json = await response.json()
                json = [json] if not isinstance(json, list) else json

                data = [Meteorology(humidity=d['current']['relative_humidity_2m'],
                                    windSpeed=d['current']['wind_speed_10m'],
                                    temperature=d['current']['temperature_2m'],
                                    windDirection=d['current']['wind_direction_10m']) for d in json]

                return data
