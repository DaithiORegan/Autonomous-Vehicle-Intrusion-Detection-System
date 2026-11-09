import os
import pandas as pd
import matplotlib.pyplot as plt


os.makedirs(
    "canSim/results/plots",
    exist_ok=True
)


def plot_signal(
    input_file,
    signal_name
):

    df = pd.read_csv(
        input_file
    )


    signal_df = df[
        df["signal_name"]
        == signal_name
    ].copy()


    benign = signal_df[
        signal_df["label"] == 0
    ]

    attack = signal_df[
        signal_df["label"] == 1
    ]


    plt.figure(
        figsize=(11, 6)
    )


    plt.scatter(
        benign["timestamp"],
        benign["signal_value"],
        s=8,
        label="Legitimate"
    )


    if len(attack) > 0:

        plt.scatter(
            attack["timestamp"],
            attack["signal_value"],
            s=15,
            label="Attack"
        )


    plt.xlabel(
        "Simulation Time (seconds)"
    )

    plt.ylabel(
        signal_name.replace(
            "_",
            " "
        ).title()
    )

    plt.title(
        "Autonomous Vehicle CAN Signal: "
        + signal_name.replace(
            "_",
            " "
        ).title()
    )

    plt.legend()

    plt.tight_layout()


    output_file = (
        "canSim/results/plots/"
        f"{signal_name}_attack.png"
    )


    plt.savefig(
        output_file,
        dpi=300
    )


    print(
        f"Saved -> {output_file}"
    )

    plt.show()


if __name__ == "__main__":

    plot_signal(
        "canSim/logs/"
        "test_spoof_combined.csv",

        "steering_angle"
    )