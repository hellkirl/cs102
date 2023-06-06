import pandas as pd
from bottle import redirect, request, route, run, template

from homework07.bayes import NaiveBayesClassifier
from homework07.db import News, session
from homework07.scraputils import get_news


def main():
    s = session()

    existing_news = [i.title for i in s.query(News).all()]
    for news in get_news("https://news.ycombinator.com/"):
        if news["title"] not in existing_news:
            s.add(News(**news))
            s.commit()


@route("/")
def news_list():
    """Homepage with unlabeled news"""
    s = session()

    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    """Adds labels to news"""
    news_id = request.query.id
    label = request.query.label

    s = session()
    news = s.query(News).filter(News.id == news_id).first()
    news.label = label
    s.commit()

    redirect("/")


@route("/update")
def update_news():
    """Updates news in the database"""
    s = session()
    existing_news = [i.title for i in s.query(News).all()]

    for news in get_news("https://news.ycombinator.com/"):
        if news["title"] not in existing_news:
            s.add(News(**news))
            s.commit()

    redirect("/")


def preprocess_string(s: str) -> str:
    """
    The function uses re to preprocess the string
    """
    import re

    # replacing non-alphabetic symbols
    cleaned_s = re.sub(r"[^a-z\s]+", " ", s, flags=re.IGNORECASE)
    # replacing multiple spaces
    cleaned_s = re.sub(r"(\s+)", " ", cleaned_s)
    # converting to lowercase
    cleaned_s = cleaned_s.lower()

    return cleaned_s


@route("/classify")
def classify_news():
    """Classifies news"""

    s = session()
    model = NaiveBayesClassifier()
    try:
        unlabeled_news = [article.title for article in s.query(News).filter(News.label == None).all()]

        labeled_news = [preprocess_string(article.title) for article in s.query(News).filter(News.label != None).all()]
        labeled_news_label = [article.label for article in s.query(News).filter(News.label != None).all()]

        model.fit(labeled_news, labeled_news_label)

        predicted_news = zip(unlabeled_news, model.predict(unlabeled_news))

        return predicted_news
    except Exception:
        pass


@route("/recommendations")
def recommendations():
    s = session()
    news = classify_news()

    for title, label in news:
        for article in s.query(News).filter(News.label == None).all():
            if article.title == title:
                article.label = label
                s.commit()

    classified_news = sorted(s.query(News).filter(News.label != "never"), key=lambda x: x.label)
    return template("news_recommendations", rows=classified_news)


if __name__ == "__main__":
    main()
    run(host="localhost", port=8080)
