from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier as dclf
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
import os
import json
from ..benchmark_wrapper import BenchmarkWrapper


class DummyClassifier(BenchmarkWrapper):
    def __init__(self):
        self.benchmarkName = "DummyClassifier"
        super().__init__(self.benchmarkName)
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []

    def getSettings(self):                                                          #TODO:takes argument for the path + change to set settings
        with open(os.path.join(self.home_dir, "../config/dummy_config.json")) as f:
            self.settings = json.load(f)
        self.celery_log.info("Settings loaded")
        self.dataset = self.settings["dataset"]
        self.metrics = self.settings["metrics"]

    def getPresets(self):
        with open(os.path.join(self.home_dir, "../config/dummy_preset.json")) as f:
            self.presets = json.load(f)
        self.celery_log.info("Presets loaded")
        self.test_split = self.presets["test_split"]

    def startBenchmark(self):
        self.getSettings()
        self.getPresets()
        print(self.dummyClf())

    def benchmarkStatus():
        # TODO: Communication with celery workers to see if the task is completed.
        pass

    def stopBenchmark():
        # Todo:Figure out stopping the benchmark
        pass

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
        self.celery_log.info("Dataset extracted")

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
        for k, v in results_dict.items():
            if k in self.metrics:
                new_results_dict[k] = v
        self.celery_log.info(f"{results_dict}")
        self.celery_log.info("Training task completed")


def run():
    DummyClassifier().startBenchmark()
