from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier as dclf
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
import json
from ..common.benchmark_wrapper import BenchmarkWrapper
from ..common.benchmark_factory import estimate_repetitions
from time import sleep


class DummyClassifier(BenchmarkWrapper):

    """
    This is a dummy benchmark class to demonstrate how to construct code for benchmark implementation.
    """

    def __init__(self):
        self.benchmarkName = "DummyClassifier"
        super().__init__(self.benchmarkName)
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []

        self.settings_loc = self.home_dir.joinpath(
            "benchmarks", "dummy_classifier", "settings"
        )

    def setSettings(self):
        with open(f"{self.settings_loc}/settings1.json") as f:
            try:
                self._settings = json.load(f)
            except ValueError:
                raise "There was a value error in importing the settings json"
            self.dataset = self.checkSettings("dataset")
            self.metrics = self.checkSettings("metrics")
            self.test_split = self.checkSettings("test_split")
            self.burnin = self.checkSettings("burnin")
            self.repetitions = self.checkSettings("repetitions")

    def startBenchmark(self):
        self.setSettings()
        return self.dummyClf()

    def benchmarkStatus():
        # TODO: Communication with celery workers to see if the task is completed.
        pass

    def __str__(self) -> str:
        return "Dummy Classifier"

    def getSettings(self):
        self.setSettings()
        if self.repetitions == None:
            self.repetitions = estimate_repetitions(self.startBenchmark)
        return [self.burnin, self.repetitions]

    def stopBenchmark():
        # TODO : Figure out stopping the benchmark
        pass

    def extractDataset(self):
        if self.dataset == "iris":
            data, target = load_iris(return_X_y=True)
        sleep(0.05)  ##Used to debug the logs
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            data,
            target,
            stratify=target,
            test_size=self.test_split,
            shuffle=True,
            random_state=42,
        )

    def dummyClf(self) -> dict:
        with BenchmarkWrapper.Timer() as t:
            dummy_clf = dclf(strategy="stratified", random_state=42)
            sleep(0.01)
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
        return {"results": new_results_dict, "Time Elapsed": "{:.4f}".format(t.elapsed)}

    def checkSettings(self, key):
        try:
            return self._settings[key]
        except KeyError:
            return None
