import os
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

os.makedirs("canSim/results", exist_ok=True)


def evaluate_results(
    result_file,
    detector_name
):

    df = pd.read_csv(result_file)

    y_true = df["label"]

    y_pred = df["predicted"]

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    ).ravel()

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    false_positive_rate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )

    detection_rate = recall

    #
    # Detection latency
    #
    attack_rows = df[
        df["label"] == 1
    ]

    detected_attacks = df[
        (df["label"] == 1)
        &
        (df["predicted"] == 1)
    ]

    if (
        len(attack_rows) > 0
        and
        len(detected_attacks) > 0
    ):

        attack_start = (
            attack_rows["timestamp"].min()
        )

        first_detection = (
            detected_attacks["timestamp"].min()
        )

        detection_latency = (
            first_detection - attack_start
        )

    else:

        detection_latency = None

    results = {
        "detector": detector_name,

        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,

        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,

        "false_positive_rate":
            false_positive_rate,

        "detection_rate":
            detection_rate,

        "detection_latency_seconds":
            detection_latency
    }

    print("\n================================")
    print(detector_name)
    print("================================")

    print(f"True Positives:  {tp}")
    print(f"True Negatives:  {tn}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")

    print()

    print(
        f"Accuracy:  {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall:    {recall:.4f}"
    )

    print(
        f"F1 Score:  {f1:.4f}"
    )

    print(
        f"False Positive Rate: "
        f"{false_positive_rate:.4f}"
    )

    print(
        f"Detection Rate: "
        f"{detection_rate:.4f}"
    )

    if detection_latency is not None:

        print(
            f"Detection Latency: "
            f"{detection_latency:.6f} seconds"
        )

    else:

        print(
            "Detection Latency: "
            "Attack was not detected."
        )

    return results


if __name__ == "__main__":

    statistical = evaluate_results(
        "canSim/results/statistical_dos.csv",
        "Statistical IDS"
    )

    isolation = evaluate_results(
        "canSim/results/isolation_forest_dos.csv",
        "Isolation Forest"
    )

    comparison = pd.DataFrame([
        statistical,
        isolation
    ])

    comparison.to_csv(
        "canSim/results/dos_comparison.csv",
        index=False
    )

    print(
        "\nComparison saved -> "
        "canSim/results/dos_comparison.csv"
    )