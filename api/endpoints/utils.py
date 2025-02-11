from pydantic import ValidationError
from fastapi import HTTPException
from typing import Callable, Coroutine, Any
from functools import wraps

def validate_input(model: type):
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                if 'request' in kwargs:
                    data = await kwargs['request'].json()
                    validated = model.model_validate(data)
                    kwargs['validated_data'] = validated
                return await func(*args, **kwargs)
            except ValidationError as e:
                raise HTTPException(422, detail=e.errors())
        return wrapper
    return decorator