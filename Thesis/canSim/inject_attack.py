import os
import csv
import random
import pandas as pd

from generate_can import value_to_payload


os.makedirs(
    "canSim/logs",
    exist_ok=True
)


# ---------------------------------------------------------
# SAVE ATTACK
# ---------------------------------------------------------

def save_attack(
    messages,
    output_file
):

    with open(
        output_file,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "timestamp",
            "can_id",
            "signal_name",
            "signal_value",
            "data",
            "dlc",
            "attack_type",
            "label"
        ])

        writer.writerows(
            messages
        )


    print(
        f"Generated {len(messages)} "
        f"attack messages -> "
        f"{output_file}"
    )


# ---------------------------------------------------------
# DOS ATTACK
# ---------------------------------------------------------

def generate_dos_attack(
    output_file,
    start_time=35,
    duration=10,
    interval=0.002,
    seed=200
):

    random.seed(seed)

    messages = []

    timestamp = start_time


    while (
        timestamp
        < start_time + duration
    ):

        # High-priority CAN IDs
        can_id = random.randint(
            0x001,
            0x00F
        )

        payload = [
            random.randint(
                0,
                255
            )
            for _ in range(8)
        ]


        messages.append([
            timestamp,
            hex(can_id),
            "bus_flood",
            0,
            payload,
            8,
            "dos",
            1
        ])


        timestamp += interval


    save_attack(
        messages,
        output_file
    )


# ---------------------------------------------------------
# STEERING SPOOF ATTACK
# ---------------------------------------------------------

def generate_spoof_attack(
    output_file,
    start_time=35,
    duration=10,
    interval=0.010,
    seed=250
):

    random.seed(seed)

    messages = []

    timestamp = start_time


    while (
        timestamp
        < start_time + duration
    ):

        # Legitimate steering CAN ID
        can_id = 0x101

        signal_name = (
            "steering_angle"
        )

        # Dangerous false steering input
        signal_value = random.uniform(
            25,
            35
        )

        payload = value_to_payload(
            signal_name,
            signal_value
        )


        messages.append([
            timestamp,
            hex(can_id),
            signal_name,
            signal_value,
            payload,
            8,
            "spoof",
            1
        ])


        timestamp += interval


    save_attack(
        messages,
        output_file
    )


# ---------------------------------------------------------
# REPLAY ATTACK
# ---------------------------------------------------------

def generate_replay_attack(
    benign_file,
    output_file,
    start_time=35,
    duration=10,
    interval=0.005,
    seed=300
):

    random.seed(seed)

    benign = pd.read_csv(
        benign_file
    )


    # Replay vehicle-control messages
    captured = benign[
        (
            benign["timestamp"]
            < start_time
        )
        &
        (
            benign["signal_name"].isin(
                [
                    "vehicle_speed",
                    "steering_angle",
                    "lane_keep_command"
                ]
            )
        )
    ].copy()


    if len(captured) == 0:

        raise ValueError(
            "No CAN frames available "
            "for replay."
        )


    messages = []

    timestamp = start_time


    while (
        timestamp
        < start_time + duration
    ):

        row = captured.sample(
            n=1,
            random_state=random.randint(
                0,
                999999
            )
        ).iloc[0]


        messages.append([
            timestamp,
            row["can_id"],
            row["signal_name"],
            row["signal_value"],
            row["data"],
            int(row["dlc"]),
            "replay",
            1
        ])


        timestamp += interval


    save_attack(
        messages,
        output_file
    )


# ---------------------------------------------------------
# BRAKE SPOOF ATTACK
# ---------------------------------------------------------

def generate_brake_spoof_attack(
    output_file,
    start_time=35,
    duration=10,
    interval=0.02,
    seed=350
):

    random.seed(seed)

    messages = []

    timestamp = start_time


    while (
        timestamp
        < start_time + duration
    ):

        can_id = 0x102

        signal_name = (
            "brake_pressure"
        )

        # False emergency braking
        signal_value = random.uniform(
            85,
            100
        )

        payload = value_to_payload(
            signal_name,
            signal_value
        )


        messages.append([
            timestamp,
            hex(can_id),
            signal_name,
            signal_value,
            payload,
            8,
            "brake_spoof",
            1
        ])


        timestamp += interval


    save_attack(
        messages,
        output_file
    )


if __name__ == "__main__":

    generate_dos_attack(
        "canSim/logs/"
        "attack_dos.csv"
    )

    generate_spoof_attack(
        "canSim/logs/"
        "attack_spoof.csv"
    )

    generate_replay_attack(
        "canSim/logs/"
        "test_benign.csv",
        "canSim/logs/"
        "attack_replay.csv"
    )

    generate_brake_spoof_attack(
        "canSim/logs/"
        "attack_brake_spoof.csv"
    )