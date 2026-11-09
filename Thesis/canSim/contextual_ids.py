import os
import pandas as pd

from features import compute_features


os.makedirs(
    "canSim/results",
    exist_ok=True
)


class ContextualAVIDS:

    def __init__(self):

        pass


    def predict(self, test_data):

        df = compute_features(
            test_data
        )

        predictions = []
        reasons = []
        severity = []

        for _, row in df.iterrows():

            attack = False
            reason_list = []
            severity_level = "LOW"

            # -------------------------------------------------
            # 1. HIGH-SPEED STEERING INCONSISTENCY
            # -------------------------------------------------

            if (
                row["ctx_speed"] > 80
                and
                abs(row["ctx_steering"]) > 20
            ):

                attack = True

                reason_list.append(
                    "Large steering angle "
                    "at high vehicle speed"
                )

                severity_level = "HIGH"

            # -------------------------------------------------
            # 2. EXTREME STEERING RATE
            # -------------------------------------------------

            if (
                row["signal_name"]
                == "steering_angle"
                and
                abs(
                    row[
                        "signal_rate_of_change"
                    ]
                ) > 500
            ):

                attack = True

                reason_list.append(
                    "Rapid steering angle change"
                )

                severity_level = "HIGH"

            # -------------------------------------------------
            # 3. LANE COMMAND / STEERING MISMATCH
            # -------------------------------------------------

            if (
                row[
                    "lane_steering_difference"
                ] > 15
                and
                row["ctx_speed"] > 50
            ):

                attack = True

                reason_list.append(
                    "Steering inconsistent "
                    "with lane-keeping command"
                )

                severity_level = "HIGH"

            # -------------------------------------------------
            # 4. BRAKE + ACCELERATOR CONFLICT
            # -------------------------------------------------

            if (
                row["ctx_brake"] > 70
                and
                row[
                    "ctx_accelerator"
                ] > 60
            ):

                attack = True

                reason_list.append(
                    "High brake and accelerator "
                    "commands simultaneously"
                )

                severity_level = "MEDIUM"

            # -------------------------------------------------
            # 5. SHORT DISTANCE AT HIGH SPEED
            # -------------------------------------------------

            if (
                row["ctx_speed"] > 70
                and
                row[
                    "ctx_object_distance"
                ] < 10
                and
                row["ctx_brake"] < 20
            ):

                attack = True

                reason_list.append(
                    "Unsafe speed-distance "
                    "relationship without braking"
                )

                severity_level = "CRITICAL"

            # -------------------------------------------------
            # FINAL DECISION
            # -------------------------------------------------

            predictions.append(
                1 if attack else 0
            )

            if len(reason_list) == 0:

                reasons.append(
                    "No contextual anomaly"
                )

            else:

                reasons.append(
                    "; ".join(
                        reason_list
                    )
                )

            severity.append(
                severity_level
            )

        df[
            "context_predicted"
        ] = predictions

        df[
            "context_reason"
        ] = reasons

        df[
            "context_severity"
        ] = severity

        return df


def run_contextual_ids(
    test_file,
    output_file
):

    test = pd.read_csv(
        test_file
    )

    ids = ContextualAVIDS()

    results = ids.predict(
        test
    )

    results.to_csv(
        output_file,
        index=False
    )

    print(
        f"Contextual IDS results -> "
        f"{output_file}"
    )


if __name__ == "__main__":

    run_contextual_ids(
        "canSim/logs/"
        "test_spoof_combined.csv",

        "canSim/results/"
        "contextual_spoof.csv"
    )