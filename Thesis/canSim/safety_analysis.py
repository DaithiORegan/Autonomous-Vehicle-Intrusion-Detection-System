import os
import pandas as pd


os.makedirs(
    "canSim/results",
    exist_ok=True
)


# ---------------------------------------------------------
# SAFETY RULES
# ---------------------------------------------------------

def evaluate_safety(row):

    signal = row[
        "signal_name"
    ]

    try:
        value = float(
            row["signal_value"]
        )
    except:
        value = 0


    # ---------------------------------------------
    # STEERING
    # ---------------------------------------------

    if signal == "steering_angle":

        if abs(value) >= 25:

            return (
                "CRITICAL",
                "Large steering command may "
                "cause sudden vehicle deviation."
            )

        elif abs(value) >= 15:

            return (
                "HIGH",
                "Abnormal steering angle "
                "could affect lane stability."
            )


    # ---------------------------------------------
    # BRAKING
    # ---------------------------------------------

    if signal == "brake_pressure":

        if value >= 80:

            return (
                "CRITICAL",
                "Unexpected emergency braking "
                "could cause loss of control "
                "or rear collision."
            )

        elif value >= 60:

            return (
                "HIGH",
                "Unexpected braking command."
            )


    # ---------------------------------------------
    # ACCELERATOR
    # ---------------------------------------------

    if (
        signal
        == "accelerator_position"
    ):

        if value >= 90:

            return (
                "CRITICAL",
                "Abnormally high accelerator "
                "command may cause "
                "unintended acceleration."
            )


    # ---------------------------------------------
    # LANE KEEPING
    # ---------------------------------------------

    if (
        signal
        == "lane_keep_command"
    ):

        if abs(value) >= 8:

            return (
                "HIGH",
                "Extreme lane-keeping command "
                "could alter vehicle trajectory."
            )


    # ---------------------------------------------
    # OBJECT DISTANCE
    # ---------------------------------------------

    if (
        signal
        == "object_distance"
    ):

        if value <= 5:

            return (
                "CRITICAL",
                "Extremely small object distance "
                "represents imminent "
                "collision risk."
            )

        elif value <= 10:

            return (
                "HIGH",
                "Object detected at unsafe "
                "following distance."
            )


    # ---------------------------------------------
    # DOS
    # ---------------------------------------------

    if signal == "bus_flood":

        return (
            "HIGH",
            "CAN bus saturation may delay "
            "time-critical vehicle-control "
            "messages."
        )


    return (
        "LOW",
        "No immediate safety-critical "
        "condition detected."
    )


# ---------------------------------------------------------
# ANALYSE FILE
# ---------------------------------------------------------

def analyse_safety(
    input_file,
    output_file
):

    df = pd.read_csv(
        input_file
    )


    severity = []
    safety_effect = []


    for _, row in df.iterrows():

        level, effect = (
            evaluate_safety(row)
        )

        severity.append(
            level
        )

        safety_effect.append(
            effect
        )


    df[
        "safety_severity"
    ] = severity

    df[
        "safety_effect"
    ] = safety_effect


    df.to_csv(
        output_file,
        index=False
    )


    print(
        f"Safety analysis saved -> "
        f"{output_file}"
    )


    print("\nSafety Severity Counts")
    print("-" * 40)

    print(
        df[
            "safety_severity"
        ].value_counts()
    )


if __name__ == "__main__":

    analyse_safety(
        "canSim/logs/"
        "test_spoof_combined.csv",

        "canSim/results/"
        "spoof_safety_analysis.csv"
    )