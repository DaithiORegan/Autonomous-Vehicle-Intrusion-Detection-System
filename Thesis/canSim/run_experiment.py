import os
import pandas as pd

from generate_can import generate_normal_traffic
from inject_attack import (
    generate_dos_attack,
    generate_spoof_attack,
    generate_replay_attack,
    generate_brake_spoof_attack
)
from build_dataset import build_test_dataset
from statistical_ids import run_statistical_ids
from isolation_forest_ids import run_isolation_forest
from evaluate import evaluate_results


os.makedirs("canSim/logs", exist_ok=True)
os.makedirs("canSim/results", exist_ok=True)


def run_experiment(
    attack_type,
    threshold_percentile=95,
    train_seed=42,
    test_seed=100
):

    print("\n" + "=" * 65)
    print(f"CAN BUS IDS EXPERIMENT: {attack_type.upper()}")
    print("=" * 65)

    # -----------------------------------------------------
    # STEP 1 - Generate benign training traffic
    # -----------------------------------------------------

    print("\nSTEP 1 - Generating benign training traffic")

    generate_normal_traffic(
        "canSim/logs/train_benign.csv",
        duration=60,
        seed=train_seed
    )

    # -----------------------------------------------------
    # STEP 2 - Generate independent benign test traffic
    # -----------------------------------------------------

    print("\nSTEP 2 - Generating benign test traffic")

    generate_normal_traffic(
        "canSim/logs/test_benign.csv",
        duration=60,
        seed=test_seed
    )

    # -----------------------------------------------------
    # STEP 3 - Generate selected attack
    # -----------------------------------------------------

    print(f"\nSTEP 3 - Generating {attack_type.upper()} attack")

    attack_file = (
        f"canSim/logs/attack_{attack_type}.csv"
    )

    if attack_type == "dos":

        generate_dos_attack(
            attack_file
        )

    elif attack_type == "spoof":

        generate_spoof_attack(
            attack_file
        )

    elif attack_type == "replay":

        generate_replay_attack(
            "canSim/logs/test_benign.csv",
            attack_file
        )

    elif attack_type == "brake_spoof":

        generate_brake_spoof_attack(
        attack_file
    )

    else:

        raise ValueError(
            "attack_type must be: "
            "dos, spoof, replay or brake_spoof"
        )

    # -----------------------------------------------------
    # STEP 4 - Combine benign + malicious traffic
    # -----------------------------------------------------

    print("\nSTEP 4 - Building combined test dataset")

    combined_file = (
        f"canSim/logs/test_{attack_type}_combined.csv"
    )

    build_test_dataset(
        "canSim/logs/test_benign.csv",
        attack_file,
        combined_file
    )

    # -----------------------------------------------------
    # STEP 5 - Statistical IDS
    # -----------------------------------------------------

    print("\nSTEP 5 - Running Statistical IDS")

    statistical_file = (
        f"canSim/results/statistical_{attack_type}.csv"
    )

    run_statistical_ids(
        "canSim/logs/train_benign.csv",
        combined_file,
        statistical_file
    )

    # -----------------------------------------------------
    # STEP 6 - Isolation Forest IDS
    # -----------------------------------------------------

    print("\nSTEP 6 - Running Isolation Forest IDS")

    isolation_file = (
        f"canSim/results/isolation_forest_{attack_type}.csv"
    )

    run_isolation_forest(
        "canSim/logs/train_benign.csv",
        combined_file,
        isolation_file,
        threshold_percentile=threshold_percentile
    )

    # -----------------------------------------------------
    # STEP 7 - Evaluate both detectors
    # -----------------------------------------------------

    print("\nSTEP 7 - Evaluating Statistical IDS")

    statistical_results = evaluate_results(
        statistical_file,
        "Statistical IDS"
    )

    print("\nSTEP 8 - Evaluating Isolation Forest")

    isolation_results = evaluate_results(
        isolation_file,
        "Isolation Forest"
    )

    # Add attack information
    statistical_results["attack_type"] = attack_type
    statistical_results["threshold_percentile"] = None

    isolation_results["attack_type"] = attack_type
    isolation_results["threshold_percentile"] = (
        threshold_percentile
    )

    # -----------------------------------------------------
    # STEP 9 - Save comparison
    # -----------------------------------------------------

    comparison = pd.DataFrame([
        statistical_results,
        isolation_results
    ])

    comparison_file = (
        f"canSim/results/{attack_type}_comparison.csv"
    )

    comparison.to_csv(
        comparison_file,
        index=False
    )

    print("\n" + "=" * 65)
    print(f"{attack_type.upper()} EXPERIMENT COMPLETE")
    print("=" * 65)

    print(
        f"\nComparison saved -> "
        f"{comparison_file}"
    )

    return comparison


if __name__ == "__main__":

    run_experiment(
        attack_type="dos",
        threshold_percentile=95
    )