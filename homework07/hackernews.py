import pandas as pd
import scipy.integrate
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

    for news in get_news("https://news.ycombinator.com/newest", n_pages=5):
        if news["title"] not in existing_news:
            s.add(News(**news))
            s.commit()

    redirect("/")


def clean(s):
    from string import punctuation

    translator = str.maketrans("", "", punctuation)
    return s.translate(translator)


@route("/classify")
def classify_news():
    """Classifies news using MultinomialNB"""

    s = session()

    model = NaiveBayesClassifier()
    unlabeled_news = [clean(article.title).lower() for article in s.query(News).filter(News.label == None).all()]
    unlabeled_news_id = [article.id for article in s.query(News).filter(News.label == None).all()]
    X, y = (
        [clean(article.title).lower() for article in s.query(News).filter(News.label != None).all()],
        [article.label for article in s.query(News).filter(News.label != None).all()],
    )
    model.fit(X, y)
    classified_news = zip(unlabeled_news_id, model.predict(unlabeled_news))

    classification = []
    for id, label in classified_news:
        for article in s.query(News).filter(News.label == None).all():
            if article.id == id:
                article_unlabeled = article
                article_unlabeled.label = label
                classification.append(article_unlabeled)

    classification.sort(key=lambda article: article.label)
    return template("news_recommendations", rows=classification)


if __name__ == "__main__":
    main()
    run(host="localhost", port=8080)
