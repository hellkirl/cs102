import nltk
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter, defaultdict


class NaiveBayesClassifier:

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.classes = None
        self.class_probabilities = None
        self.word_probabilities = None
        self.vectorizer = CountVectorizer(ngram_range=(1, 2))
        self.lemmatizer = WordNetLemmatizer()

    def fit(self, X, y):
        """ Fit Naive Bayes classifier according to X, y. """
        X_lemmatized = self.lemmatize_documents(X)
        X_vectorized = self.vectorizer.fit_transform(X_lemmatized)

        self.classes = list(set(y))
        self.class_probabilities = self.calculate_class_probabilities(y)

        word_counts = defaultdict(Counter)
        class_counts = Counter()

        for i, label in enumerate(y):
            doc = X_vectorized[i]
            class_counts[label] += 1
            for word, count in zip(self.vectorizer.get_feature_names_out(), doc.toarray()[0]):
                word_counts[label][word] += count

        self.word_probabilities = defaultdict(Counter)

        for label in self.classes:
            total_words = sum(word_counts[label].values())
            for word in word_counts[label]:
                self.word_probabilities[label][word] = (word_counts[label][word] + self.alpha) / (
                            total_words + self.alpha * len(word_counts[label]))

    def predict(self, X):
        """ Perform classification on an array of test vectors X. """
        X_lemmatized = self.lemmatize_documents(X)
        X_vectorized = self.vectorizer.transform(X_lemmatized)

        predictions = []
        for doc in X_vectorized:
            scores = defaultdict(float)
            for label in self.classes:
                score = self.class_probabilities[label]
                for word, count in zip(self.vectorizer.get_feature_names_out(), doc.toarray()[0]):
                    score *= self.word_probabilities[label][word] ** count
                scores[label] = score
            predicted_label = max(scores, key=scores.get)
            predictions.append(predicted_label)

        return predictions

    def score(self, X_test, y_test):
        """ Returns the mean accuracy on the given test data and labels. """
        predictions = self.predict(X_test)
        correct = sum(1 for pred, true in zip(predictions, y_test) if pred == true)
        accuracy = correct / len(y_test)
        return accuracy

    def lemmatize_documents(self, documents):
        lemmatized_documents = []
        for doc in documents:
            lemmatized_words = [self.lemmatizer.lemmatize(word) for word in nltk.word_tokenize(doc)]
            lemmatized_documents.append(' '.join(lemmatized_words))
        return lemmatized_documents

    def calculate_class_probabilities(self, y):
        class_counts = Counter(y)
        total_samples = len(y)
        class_probabilities = {}

        for label, count in class_counts.items():
            class_probabilities[label] = count / total_samples

        return class_probabilities
