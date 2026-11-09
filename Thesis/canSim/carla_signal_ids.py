import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score
)


BENIGN_FILE = Path(
    r"C:\Users\gripx\Downloads\DaithiORegan_FYP_Code"
    r"\canSim\logs\carla_telemetry.csv"
)

ATTACK_ROOT = Path(
    "canSim/logs/carla_validation"
)

OUTPUT_FILE = (
    ATTACK_ROOT /
    "carla_signal_ids_results.csv"
)

ATTACK_FILES = {
    "spoof":
        ATTACK_ROOT / "carla_spoof.csv",

    "replay":
        ATTACK_ROOT / "carla_replay.csv",

    "dos":
        ATTACK_ROOT / "carla_dos.csv"
}



benign = pd.read_csv(
    BENIGN_FILE
)

benign["value"] = pd.to_numeric(
    benign["value"],
    errors="coerce"
)

benign["timestamp"] = pd.to_numeric(
    benign["timestamp"],
    errors="coerce"
)

benign = benign.dropna(
    subset=[
        "timestamp",
        "can_id",
        "value"
    ]
)



profiles = {}


for can_id, group in benign.groupby(
    "can_id"
):

    group = group.sort_values(
        "timestamp"
    )

    values = (
        group["value"]
        .dropna()
    )

    intervals = (
        group["timestamp"]
        .diff()
        .dropna()
    )

    profiles[str(can_id)] = {

        "mean":
            values.mean(),

        "std":
            max(
                values.std(),
                1e-6
            ),

        "min":
            values.min(),

        "max":
            values.max(),

        "median_interval":
            intervals.median()
            if len(intervals) > 0
            else 0.05
    }


print("=" * 75)
print("CARLA BENIGN SIGNAL PROFILES")
print("=" * 75)

for can_id, profile in profiles.items():

    print(
        f"{can_id} | "
        f"mean={profile['mean']:.4f} | "
        f"std={profile['std']:.4f} | "
        f"range={profile['min']:.4f} "
        f"to {profile['max']:.4f} | "
        f"interval="
        f"{profile['median_interval']:.4f}s"
    )


def detect(df):

    predictions = []

    # Store previous timestamp separately
    # for each CAN identifier.
    previous_timestamp = {}

    for _, row in df.iterrows():

        can_id = str(
            row["can_id"]
        )

        value = float(
            row["value"]
        )

        timestamp = float(
            row["timestamp"]
        )

        anomalous = False

        if can_id not in profiles:

            anomalous = True

        else:

            profile = profiles[
                can_id
            ]


            z_score = abs(
                value
                -
                profile["mean"]
            ) / profile["std"]


            if z_score > 5.0:

                anomalous = True


        

            if can_id in previous_timestamp:

                interval = (
                    timestamp
                    -
                    previous_timestamp[
                        can_id
                    ]
                )

                expected_interval = (
                    profile[
                        "median_interval"
                    ]
                )

                # Replay/flood messages occurring much
                # faster than this CAN signal normally
                # appears are considered suspicious.
                if (
                    expected_interval > 0
                    and interval
                    <
                    expected_interval * 0.40
                ):

                    anomalous = True


      
        previous_timestamp[
            can_id
        ] = timestamp


        predictions.append(
            1 if anomalous else 0
        )


    return np.array(
        predictions
    )




def evaluate(
    attack_name,
    file_path
):

    df = pd.read_csv(
        file_path
    )

    df["timestamp"] = pd.to_numeric(
        df["timestamp"],
        errors="coerce"
    )

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "timestamp",
            "can_id",
            "value",
            "label"
        ]
    )

    df = df.sort_values(
        "timestamp"
    ).reset_index(
        drop=True
    )

    y_true = (
        df["label"]
        .astype(int)
    )

    y_pred = detect(
        df
    )


    tn, fp, fn, tp = confusion_matrix(
        y_true,
        y_pred,
        labels=[0, 1]
    ).ravel()


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

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    fpr = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else 0
    )


    return {

        "attack":
            attack_name,

        "TP":
            tp,

        "TN":
            tn,

        "FP":
            fp,

        "FN":
            fn,

        "accuracy":
            accuracy,

        "precision":
            precision,

        "recall":
            recall,

        "f1":
            f1,

        "fpr":
            fpr
    }




rows = []


for attack_name, path in (
    ATTACK_FILES.items()
):

    result = evaluate(
        attack_name,
        path
    )

    rows.append(
        result
    )


results = pd.DataFrame(
    rows
)


results.to_csv(
    OUTPUT_FILE,
    index=False
)




print()
print("=" * 95)
print("CARLA SIGNAL-AWARE IDS RESULTS")
print("=" * 95)

print(
    results.to_string(
        index=False
    )
)

print()
print(
    "Saved ->",
    OUTPUT_FILE
)