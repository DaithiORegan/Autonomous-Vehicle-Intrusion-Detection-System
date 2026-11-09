import os
import pandas as pd

from run_experiment import run_experiment


os.makedirs("canSim/results", exist_ok=True)


ATTACKS = [
    "dos",
    "spoof",
    "replay"
]


def run_all_attacks():

    all_results = []

    print("\n" + "=" * 70)
    print("RUNNING COMPLETE CAN BUS ATTACK EXPERIMENT")
    print("=" * 70)

    for attack in ATTACKS:

        print("\n\n")
        print("#" * 70)
        print(f"STARTING ATTACK: {attack.upper()}")
        print("#" * 70)

        comparison = run_experiment(
            attack_type=attack,
            threshold_percentile=95
        )

        all_results.append(
            comparison
        )

    # Combine all attack results
    final_results = pd.concat(
        all_results,
        ignore_index=True
    )

    output_file = (
        "canSim/results/"
        "all_attack_comparison.csv"
    )

    final_results.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 70)
    print("ALL ATTACK EXPERIMENTS COMPLETE")
    print("=" * 70)

    print(
        f"\nFinal results saved -> "
        f"{output_file}"
    )

    print("\nFINAL COMPARISON")
    print("-" * 70)

    print(
        final_results[
            [
                "attack_type",
                "detector",
                "accuracy",
                "precision",
                "recall",
                "f1_score",
                "false_positive_rate"
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":

    run_all_attacks()