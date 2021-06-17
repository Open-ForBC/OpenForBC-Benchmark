from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier as dclf
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score


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
        for k, v in results_dict.items():
            if k in self.metrics:
                new_results_dict[k] = v
        return new_results_dict


if __name__ == "__main__":
    clf = DummyClassifier()
    print(clf.dummyClf())
