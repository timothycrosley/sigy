from datetime import datetime
from typing import NamedTuple

from flask import Flask

import sigy

app = Flask(__name__)
BASE_ARTICAL_URL = "/<year>/<month>/<day>/<id>/<slug>"


class Article(NamedTuple):
    id: int
    created: datetime
    slug: str
    text: str = "Article Text"
    comments: tuple[str, ...] = ("one", "two")


def load_article(year: int, month: int, day: int, id: int, slug: str) -> Article:
    return Article(id=id, created=datetime(year=year, month=month, day=day), slug=slug)


@app.route(f"{BASE_ARTICAL_URL}/content")
@sigy.inject(article=load_article)
def article_content(article: Article) -> str:
    return article.content


@app.route(f"{BASE_ARTICAL_URL}/comments")
@sigy.inject(article=load_article)
def article_comments(article: Article) -> tuple[str, ...]:
    return article.comments
