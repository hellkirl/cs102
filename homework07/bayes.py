from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class NaiveBayesClassifier:
    """This class is a pipeline for Naive Bayes classifier"""

    def __init__(self) -> None:
        self.steps = [("cv", CountVectorizer()), ("nb_model", MultinomialNB())]
        self.pipeline = Pipeline(self.steps)

    def fit(self, X, y) -> None:
        """Fit Naive Bayes classifier according to X, y."""
        self.pipeline.fit(X, y)

    def predict(self, X):
        """Perform classification on an array of test vectors X."""
        return self.pipeline.predict(X)

    def score(self, X_test, y_test):
        """Returns the mean accuracy on the given test data and labels."""
        return self.pipeline.score(X_test, y_test)
