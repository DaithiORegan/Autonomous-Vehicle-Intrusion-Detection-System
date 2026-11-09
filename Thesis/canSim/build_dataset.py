import os
import pandas as pd

os.makedirs("canSim/logs", exist_ok=True)


def build_test_dataset(
    benign_file,
    attack_file,
    output_file
):

    benign = pd.read_csv(benign_file)
    attack = pd.read_csv(attack_file)

    combined = pd.concat(
        [benign, attack],
        ignore_index=True
    )

    
    combined = combined.sort_values(
        by="timestamp"
    ).reset_index(drop=True)

    combined.to_csv(
        output_file,
        index=False
    )

    print("\nDataset created")
    print("----------------------")
    print(f"Benign messages: {len(benign)}")
    print(f"Attack messages: {len(attack)}")
    print(f"Total messages:  {len(combined)}")
    print(f"Saved -> {output_file}")


if __name__ == "__main__":

    build_test_dataset(
        "canSim/logs/test_benign.csv",
        "canSim/logs/attack_dos.csv",
        "canSim/logs/test_dos_combined.csv"
    )