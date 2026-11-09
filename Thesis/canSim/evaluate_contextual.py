import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


def evaluate_contextual(
    result_file
):

    df = pd.read_csv(
        result_file
    )

    y_true = df["label"]

    y_pred = df[
        "context_predicted"
    ]

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

    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )

    print("\n")
    print("=" * 55)
    print("CONTEXT-AWARE AV IDS")
    print("=" * 55)

    print(
        f"True Positives:  {tp}"
    )

    print(
        f"True Negatives:  {tn}"
    )

    print(
        f"False Positives: {fp}"
    )

    print(
        f"False Negatives: {fn}"
    )

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
        f"FPR:       {fpr:.4f}"
    )


if __name__ == "__main__":

    evaluate_contextual(
        "canSim/results/"
        "contextual_spoof.csv"
    )