from collections import defaultdict

import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB


class NaiveBayesClassifier:
    def __init__(self, lemmatize=False, stem=False, ngram_range=(1, 1)):
        self.class_probabilities = defaultdict(float)
        self.feature_probabilities = defaultdict(lambda: defaultdict(float))
        self.classes = set()
        self.lemmatize = lemmatize
        self.stem = stem
        self.ngram_range = ngram_range
        self.stopwords = set(stopwords.words("english"))

    def preprocess_text(self, text):
        tokens = word_tokenize(text.lower())

        if self.lemmatize:
            lemmatizer = nltk.WordNetLemmatizer()
            tokens = [lemmatizer.lemmatize(token) for token in tokens]

        if self.stem:
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(token) for token in tokens]

        tokens = [token for token in tokens if token.isalnum() and token not in self.stopwords]

        return " ".join(tokens)

    def fit(self, X, y, alpha=1.0):
        # Count occurrences of each class
        class_counts = defaultdict(int)
        for label in y:
            class_counts[label] += 1

        # Calculate class probabilities
        total_samples = len(y)
        for label, count in class_counts.items():
            self.class_probabilities[label] = count / total_samples
            self.classes.add(label)

        # Vectorize the input documents
        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(X)

        # Count occurrences of each feature by class
        for i, label in enumerate(y):
            features = X[i].nonzero()[1]
            for feature in features:
                self.feature_probabilities[label][feature] += 1

        # Calculate feature probabilities by class with smoothing
        for label in self.classes:
            total_features = sum(self.feature_probabilities[label].values())
            for feature in vectorizer.vocabulary_.keys():
                feature_count = self.feature_probabilities[label][feature]
                self.feature_probabilities[label][feature] = (feature_count + alpha) / (
                        total_features + alpha * len(vectorizer.vocabulary_)
                )

    def predict(self, X):
        predictions = []
        vectorizer = CountVectorizer(
            vocabulary=self.feature_probabilities.keys(),
            preprocessor=self.preprocess_text,
            ngram_range=self.ngram_range,
        )
        X = vectorizer.fit_transform(X)

        for i in range(X.shape[0]):
            features = X[i].nonzero()[1]
            class_scores = defaultdict(float)

            for label in self.classes:
                log_probability = np.log(self.class_probabilities[label])

                for feature in features:
                    log_probability += np.log(self.feature_probabilities[label][feature])

                class_scores[label] = log_probability

            predicted_label = max(class_scores, key=class_scores.get)
            predictions.append(predicted_label)

        return predictions

    def score(self, X, y):
        y_pred = self.predict(X)
        correct_predictions = sum(1 for y_true, y_pred in zip(y, y_pred) if y_true == y_pred)
        return correct_predictions / len(y)
