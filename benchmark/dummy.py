from typing import List
from sklearn.datasets import load_iris,load_boston
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier as dclf
from sklearn.dummy import DummyRegressor as dreg
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score, mean_absolute_error
import time

class DummyClassifier:
    def __init__(self, settings: dict, preset: dict):
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []
        self.task = settings["task"]
        self.dataset = settings["dataset"]
        self.metrics = settings["metrics"]
        self.test_split = preset["test_split"]

    def extractDataset(self):
        if self.dataset == "iris":
            data, target = load_iris(return_X_y=True)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            data,
            target,
            stratify=target,
            test_size=self.test_split,
            shuffle=True,
            random_state=42,
        )

    def dummyClf(self) -> dict:
        dummy_clf = dclf(strategy="stratified", random_state=42)
        self.extractDataset()
        dummy_clf.fit(self.X_train, self.y_train)
        y_pred = dummy_clf.predict(self.X_test)
        new_results_dict = {}
        results_dict = {
            "accuracy": accuracy_score(self.y_test, y_pred),
            "recall": recall_score(self.y_test, y_pred, average="weighted"),
            "precision": precision_score(self.y_test, y_pred, average="weighted"),
            "f1_score": f1_score(self.y_test, y_pred, average="weighted"),
        }
        time.sleep(0.1)
        for k, v in results_dict.items():
            if k in self.metrics:
                new_results_dict[k] = v
        return new_results_dict


class DummyRegressor:
    def __init__(self):
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []

    def extractDataset(self):
        data, target = load_boston(return_X_y=True)
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            data,
            target,
            test_size=0.20,
            shuffle=True,
            random_state=42,
        )

    def dummyReg(self) -> dict:
        dummy_reg = dreg(strategy="mean")
        self.extractDataset()
        dummy_reg.fit(self.X_train, self.y_train)
        y_pred = dummy_reg.predict(self.X_test)
        results_dict = {
            "score": dummy_reg.score(self.y_test, y_pred),
            "Mean absolute error": mean_absolute_error(self.y_test, y_pred)
        }
        time.sleep(0.1)
        return results_dict

