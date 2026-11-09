import os
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from isolation_forest_ids import IsolationForestIDS


# ---------------------------------------------------------
# FOLDERS
# ---------------------------------------------------------

os.makedirs("canSim/results", exist_ok=True)
os.makedirs("canSim/results/plots", exist_ok=True)


# ---------------------------------------------------------
# THRESHOLDS TO TEST
# ---------------------------------------------------------

THRESHOLDS = [
    85,
    87.5,
    90,
    92,
    94,
    95,
    96,
    97,
    98,
    99,
    99.5
]


# ---------------------------------------------------------
# CALCULATE METRICS
# ---------------------------------------------------------

def calculate_metrics(df, percentile):

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

    if (fp + tn) > 0:
        false_positive_rate = fp / (fp + tn)
    else:
        false_positive_rate = 0

    return {
        "threshold_percentile": percentile,

        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,

        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "false_positive_rate": false_positive_rate
    }


# ---------------------------------------------------------
# RUN THRESHOLD SWEEP
# ---------------------------------------------------------

def run_threshold_sweep():

    train = pd.read_csv(
        "canSim/logs/train_benign.csv"
    )

    test = pd.read_csv(
        "canSim/logs/test_dos_combined.csv"
    )

    all_results = []

    print("\n" + "=" * 60)
    print("ISOLATION FOREST THRESHOLD SWEEP")
    print("=" * 60)

    for percentile in THRESHOLDS:

        print(
            f"\nTesting threshold percentile: "
            f"{percentile}%"
        )

        # Create new Isolation Forest IDS
        model = IsolationForestIDS(
            threshold_percentile=percentile
        )

        # Train ONLY on benign traffic
        model.fit(train)

        # Test on benign + DoS traffic
        predictions = model.predict(test)

        # Calculate metrics
        metrics = calculate_metrics(
            predictions,
            percentile
        )

        all_results.append(metrics)

        print("-" * 40)

        print(
            f"TP: {metrics['true_positive']}"
        )

        print(
            f"TN: {metrics['true_negative']}"
        )

        print(
            f"FP: {metrics['false_positive']}"
        )

        print(
            f"FN: {metrics['false_negative']}"
        )

        print(
            f"Accuracy:  "
            f"{metrics['accuracy']:.4f}"
        )

        print(
            f"Precision: "
            f"{metrics['precision']:.4f}"
        )

        print(
            f"Recall:    "
            f"{metrics['recall']:.4f}"
        )

        print(
            f"F1 Score:  "
            f"{metrics['f1_score']:.4f}"
        )

        print(
            f"FPR:       "
            f"{metrics['false_positive_rate']:.4f}"
        )

    # Convert results into DataFrame
    results_df = pd.DataFrame(
        all_results
    )

    # Save CSV
    output_file = (
        "canSim/results/"
        "isolation_threshold_sweep.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 60)

    print(
        f"Threshold sweep saved -> "
        f"{output_file}"
    )

    return results_df


# ---------------------------------------------------------
# CHOOSE BEST THRESHOLD
# ---------------------------------------------------------

def choose_best_threshold(
    results_df,
    minimum_recall=0.80
):

    print("\n" + "=" * 60)
    print("SELECTING BEST THRESHOLD")
    print("=" * 60)

    # First only consider thresholds where recall
    # is at least the required minimum.
    acceptable = results_df[
        results_df["recall"] >= minimum_recall
    ]

    if len(acceptable) > 0:

        # Of acceptable thresholds,
        # choose the one with highest F1.
        best_index = (
            acceptable["f1_score"].idxmax()
        )

        best = acceptable.loc[
            best_index
        ]

        print(
            f"\nBest threshold with recall >= "
            f"{minimum_recall:.0%}"
        )

    else:

        # If none achieve 80% recall,
        # simply take highest F1 overall.
        best_index = (
            results_df["f1_score"].idxmax()
        )

        best = results_df.loc[
            best_index
        ]

        print(
            "\nWARNING: No threshold achieved "
            f"{minimum_recall:.0%} recall."
        )

        print(
            "Using highest F1 score instead."
        )

    print("\nBEST ISOLATION FOREST CONFIGURATION")
    print("-" * 45)

    print(
        f"Threshold percentile: "
        f"{best['threshold_percentile']}"
    )

    print(
        f"Accuracy: "
        f"{best['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{best['precision']:.4f}"
    )

    print(
        f"Recall: "
        f"{best['recall']:.4f}"
    )

    print(
        f"F1 Score: "
        f"{best['f1_score']:.4f}"
    )

    print(
        f"False Positive Rate: "
        f"{best['false_positive_rate']:.4f}"
    )

    print(
        f"True Positives: "
        f"{int(best['true_positive'])}"
    )

    print(
        f"True Negatives: "
        f"{int(best['true_negative'])}"
    )

    print(
        f"False Positives: "
        f"{int(best['false_positive'])}"
    )

    print(
        f"False Negatives: "
        f"{int(best['false_negative'])}"
    )

    # Save best threshold separately
    best_df = pd.DataFrame(
        [best]
    )

    best_df.to_csv(
        "canSim/results/"
        "best_isolation_threshold.csv",
        index=False
    )

    return best


# ---------------------------------------------------------
# CREATE PERFORMANCE GRAPH
# ---------------------------------------------------------

def create_metric_plot(results_df):

    x = results_df[
        "threshold_percentile"
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        x,
        results_df["accuracy"],
        marker="o",
        label="Accuracy"
    )

    plt.plot(
        x,
        results_df["precision"],
        marker="o",
        label="Precision"
    )

    plt.plot(
        x,
        results_df["recall"],
        marker="o",
        label="Recall"
    )

    plt.plot(
        x,
        results_df["f1_score"],
        marker="o",
        label="F1 Score"
    )

    plt.xlabel(
        "Isolation Forest Threshold Percentile"
    )

    plt.ylabel(
        "Metric Score"
    )

    plt.title(
        "Isolation Forest Threshold Performance"
    )

    plt.legend()

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        "canSim/results/plots/"
        "isolation_threshold_metrics.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    print(
        f"\nSaved metric graph -> "
        f"{output_file}"
    )

    plt.show()


# ---------------------------------------------------------
# CREATE FALSE POSITIVE GRAPH
# ---------------------------------------------------------

def create_fpr_plot(results_df):

    x = results_df[
        "threshold_percentile"
    ]

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        x,
        results_df[
            "false_positive_rate"
        ],
        marker="o"
    )

    plt.xlabel(
        "Isolation Forest Threshold Percentile"
    )

    plt.ylabel(
        "False Positive Rate"
    )

    plt.title(
        "Threshold vs False Positive Rate"
    )

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        "canSim/results/plots/"
        "isolation_threshold_fpr.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    print(
        f"Saved FPR graph -> "
        f"{output_file}"
    )

    plt.show()


# ---------------------------------------------------------
# CREATE F1 VS FPR GRAPH
# ---------------------------------------------------------

def create_tradeoff_plot(results_df):

    plt.figure(
        figsize=(10, 6)
    )

    plt.plot(
        results_df[
            "false_positive_rate"
        ],
        results_df[
            "f1_score"
        ],
        marker="o"
    )

    # Add threshold labels beside points
    for _, row in results_df.iterrows():

        plt.annotate(
            str(
                row[
                    "threshold_percentile"
                ]
            ),
            (
                row[
                    "false_positive_rate"
                ],
                row[
                    "f1_score"
                ]
            )
        )

    plt.xlabel(
        "False Positive Rate"
    )

    plt.ylabel(
        "F1 Score"
    )

    plt.title(
        "Isolation Forest Detection Trade-off"
    )

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    output_file = (
        "canSim/results/plots/"
        "isolation_f1_fpr_tradeoff.png"
    )

    plt.savefig(
        output_file,
        dpi=300
    )

    print(
        f"Saved trade-off graph -> "
        f"{output_file}"
    )

    plt.show()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    results = run_threshold_sweep()

    best = choose_best_threshold(
        results,
        minimum_recall=0.80
    )

    create_metric_plot(
        results
    )

    create_fpr_plot(
        results
    )

    create_tradeoff_plot(
        results
    )

    print("\n" + "=" * 60)
    print("THRESHOLD ANALYSIS COMPLETE")
    print("=" * 60)