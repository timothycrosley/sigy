"""Example of using sigy with hug

run using hug -f hug_api.py
"""
from datetime import datetime
from typing import NamedTuple

import hug

import sigy


class Article(NamedTuple):
    id: int
    created: datetime
    slug: str
    text: str = "Article Text"
    comments: tuple[str, ...] = ("one", "two")


def load_article(year: int, month: int, day: int, id: int, slug: str) -> Article:
    return Article(id=id, created=datetime(year=year, month=month, day=day), slug=slug)


@hug.get()
@sigy.inject(article=load_article)
def article_content(article: Article) -> str:
    return article.content


@hug.get()
@sigy.inject(article=load_article)
def article_comments(article: Article) -> tuple[str, ...]:
    return article.comments
