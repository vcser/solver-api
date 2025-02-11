from prometheus_client import Counter, Histogram, Gauge
import time
from functools import wraps
from typing import Callable, Any

# Métricas Prometheus
PREDICTION_METRICS = Histogram(
    'prediction_execution_seconds',
    'Prediction execution time',
    ['version', 'num_incendios', 'num_recursos']
)

PREDICTION_ERRORS = Counter(
    'prediction_errors_total',
    'Total prediction errors',
    ['type']
)

def monitor_execution_time(func: Callable[..., Any]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            return result
        except Exception as e:
            PREDICTION_ERRORS.labels(type=e.__class__.__name__).inc()
            raise
        finally:
            execution_time = time.time() - start_time
            if hasattr(args[0], 'solver_version'):
                PREDICTION_METRICS.labels(
                    version=args[0].solver_version,
                    num_incendios=len(kwargs.get('data', {}).get('incendios', [])),
                    num_recursos=len(kwargs.get('data', {}).get('recursos', []))
                ).observe(execution_time)
    return wrapper