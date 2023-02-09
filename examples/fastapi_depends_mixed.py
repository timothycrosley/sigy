"""sigy can act as a framework agnostic replacement for dependencies
See: https://fastapi.tiangolo.com/tutorial/dependencies/#dependencies-first-steps

Run with uvicorn fastapi_depends_mixed:app --reload
then go to: http://localhost:8000/docs with your browser.
"""
from __future__ import annotations

from fastapi import FastAPI

import sigy

app = FastAPI()


async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

def other_common_parameters(name: str = "Name"):
    return {"name": name}


@app.get("/items/")
@sigy.inject(commons=common_parameters, other_commons=other_common_parameters)
async def read_items(commons: dict, other_commons: dict):
    return {**commons, **other_commons}


@app.get("/users/")
@sigy.inject(commons=common_parameters, other_commons=other_common_parameters)
def read_users(commons: dict, other_commons: dict):
    return {**commons, **other_commons}
