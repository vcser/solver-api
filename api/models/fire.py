from .geography import Geography
from .meteorology import Meteorology
from .data import RequestDataPoint

class Fire(RequestDataPoint, Geography, Meteorology):
    builtLineLength: float = 0.0
    timestamp: str
