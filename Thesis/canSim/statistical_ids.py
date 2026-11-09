import os
import pandas as pd

from features import compute_features

os.makedirs("canSim/results", exist_ok=True)


class StatisticalIDS:

    def __init__(self, std_multiplier=3):

        self.std_multiplier = std_multiplier

        self.known_ids = None

        self.bus_rate_threshold = None

        self.payload_mean_min = None
        self.payload_mean_max = None

        self.payload_change_threshold = None


    def fit(self, benign_data):

        df = compute_features(benign_data)

        #
        # Learn which CAN IDs normally exist.
        #
        self.known_ids = set(
            df["can_id"].unique()
        )

        #
        # Learn normal bus traffic rate.
        #
        mean_rate = df["bus_rate_1s"].mean()

        std_rate = df["bus_rate_1s"].std()

        self.bus_rate_threshold = (
            mean_rate
            + self.std_multiplier * std_rate
        )

        #
        # Learn normal payload distribution.
        #
        mean_payload = df["payload_mean"].mean()

        std_payload = df["payload_mean"].std()

        self.payload_mean_min = (
            mean_payload
            - self.std_multiplier * std_payload
        )

        self.payload_mean_max = (
            mean_payload
            + self.std_multiplier * std_payload
        )

        #
        # Payload-change threshold.
        #
        mean_change = df["payload_change"].mean()

        std_change = df["payload_change"].std()

        self.payload_change_threshold = (
            mean_change
            + self.std_multiplier * std_change
        )

        print("\nStatistical IDS trained")

        print(
            f"Bus-rate threshold: "
            f"{self.bus_rate_threshold:.2f}"
        )

        print(
            f"Payload change threshold: "
            f"{self.payload_change_threshold:.2f}"
        )


    def predict(self, test_data):

        df = compute_features(test_data)

        predictions = []

        for _, row in df.iterrows():

            anomaly = False

            #
            # Rule 1:
            # Previously unseen CAN ID.
            #
            if row["can_id"] not in self.known_ids:
                anomaly = True

            #
            # Rule 2:
            # Abnormally high bus traffic.
            #
            if (
                row["bus_rate_1s"]
                > self.bus_rate_threshold
            ):
                anomaly = True

            #
            # Rule 3:
            # Abnormal payload mean.
            #
            if (
                row["payload_mean"]
                < self.payload_mean_min
                or
                row["payload_mean"]
                > self.payload_mean_max
            ):
                anomaly = True

            #
            # Rule 4:
            # Sudden payload change.
            #
            if (
                row["payload_change"]
                > self.payload_change_threshold
            ):
                anomaly = True

            predictions.append(
                1 if anomaly else 0
            )

        df["predicted"] = predictions

        return df


def run_statistical_ids(
    train_file,
    test_file,
    output_file
):

    train = pd.read_csv(train_file)

    test = pd.read_csv(test_file)

    ids = StatisticalIDS(
        std_multiplier=3
    )

    ids.fit(train)

    results = ids.predict(test)

    results.to_csv(
        output_file,
        index=False
    )

    print(
        f"Statistical IDS results -> "
        f"{output_file}"
    )


if __name__ == "__main__":

    run_statistical_ids(
        "canSim/logs/train_benign.csv",
        "canSim/logs/test_dos_combined.csv",
        "canSim/results/statistical_dos.csv"
    )