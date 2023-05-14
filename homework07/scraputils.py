import re

import requests
from bs4 import BeautifulSoup  # type: ignore


def extract_news(parser: object) -> list[dict[str, str]]:
    """Extract news from a given web page"""

    response = requests.get("https://news.ycombinator.com/")

    titles = list(map(lambda title: title.get_text(), parser.find_all("span", class_="titleline")))  # type: ignore
    authors = list(map(lambda author: author.get_text(), parser.find_all("a", class_="hnuser")))  # type: ignore
    points = list(map(lambda score: score.get_text(), parser.find_all("span", class_="score")))  # type: ignore
    comments = list(map(lambda comment: comment.replace("&nbsp;", ""), re.findall(r"\d*&nbsp;", response.text)))
    url = list(
        map(
            lambda span: span.find_all("a", href=True)[0]["href"],  # type: ignore
            parser.find_all("span", class_="titleline"),  # type: ignore
        )
    )

    news_list = [
        {
            "title": title[: title.find(" (")],
            "author": author,
            "points": score[: score.find(" p")],
            "comments": comment,
            "url": link,
        }
        for title, author, score, comment, link in list(zip(titles, authors, points, comments, url))
    ]

    return news_list


def extract_next_page(parser: object) -> list[dict[str, str]]:  # type: ignore
    """Extract next page URL"""
    more_link = parser.find("a", {"class": "morelink"})  # type: ignore
    if more_link:
        next_page_url = more_link["href"]
        return next_page_url


def get_news(url: str, n_pages=1) -> list[dict[str, str]]:
    """Collect news from a given web page"""
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page  # type: ignore
        news.extend(news_list)
        n_pages -= 1
    return news
