import os
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from features import (
    compute_features,
    FEATURE_COLUMNS
)

os.makedirs("canSim/results", exist_ok=True)


class IsolationForestIDS:

    def __init__(self, threshold_percentile=99):

        self.threshold_percentile = threshold_percentile

        self.scaler = StandardScaler()

        self.model = IsolationForest(
            n_estimators=200,
            contamination="auto",
            random_state=42
        )

        self.threshold = None


    def fit(self, benign_data):

        df = compute_features(benign_data)

        X = df[FEATURE_COLUMNS]

        X_scaled = self.scaler.fit_transform(X)

        self.model.fit(X_scaled)

        benign_scores = -self.model.score_samples(
            X_scaled
        )

        self.threshold = np.percentile(
            benign_scores,
            self.threshold_percentile
        )

        print("\nIsolation Forest trained")
        print(f"Training messages: {len(df)}")
        print(
            f"Threshold percentile: "
            f"{self.threshold_percentile}"
        )
        print(
            f"Threshold value: "
            f"{self.threshold:.6f}"
        )


    def predict(self, test_data):

        df = compute_features(test_data)

        X = df[FEATURE_COLUMNS]

        X_scaled = self.scaler.transform(X)

        anomaly_score = -self.model.score_samples(
            X_scaled
        )

        df["anomaly_score"] = anomaly_score

        df["predicted"] = (
            df["anomaly_score"]
            > self.threshold
        ).astype(int)

        return df


def run_isolation_forest(
    train_file,
    test_file,
    output_file,
    threshold_percentile=95
):

    train = pd.read_csv(train_file)
    test = pd.read_csv(test_file)

    ids = IsolationForestIDS(
        threshold_percentile=threshold_percentile
    )

    ids.fit(train)

    results = ids.predict(test)

    results.to_csv(
        output_file,
        index=False
    )

    print(
        f"Isolation Forest results -> "
        f"{output_file}"
    )