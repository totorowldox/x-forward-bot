from pydantic import BaseModel, field_validator
import json


class Config(BaseModel):
    """Plugin Config Here"""
    interval_seconds: int = 300

    """Subscribe X Users(USE SCREENNAME): [subscribed group ids]"""
    subscribe_x_users: dict[str, list[int]]

    @field_validator('subscribe_x_users')
    @classmethod
    def parse_subscribe_x_users(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v