import os
import csv
import random
import math

os.makedirs("canSim/logs", exist_ok=True)

CAN_CONFIG = {

    0x100: {
        "name": "vehicle_speed",
        "interval": 0.010
    },

    0x101: {
        "name": "steering_angle",
        "interval": 0.020
    },

    0x102: {
        "name": "brake_pressure",
        "interval": 0.050
    },

    0x103: {
        "name": "accelerator_position",
        "interval": 0.050
    },

    0x104: {
        "name": "lane_keep_command",
        "interval": 0.020
    },

    0x105: {
        "name": "object_distance",
        "interval": 0.050
    }
}

def generate_vehicle_speed(t):
    value = (
        65
        + 8 * math.sin(t / 8)
        + random.uniform(-1, 1)
    )

    return max(
        0,
        min(120, value)
    )


def generate_steering_angle(t):
    value = (
        3 * math.sin(t / 3)
        + random.uniform(-0.5, 0.5)
    )

    return max(
        -35,
        min(35, value)
    )


def generate_brake_pressure(t):
    if 20 < t < 23 or 45 < t < 48:

        value = (
            40
            + random.uniform(-5, 5)
        )

    else:

        value = random.uniform(0, 4)

    return max(
        0,
        min(100, value)
    )


def generate_accelerator_position(t):

    value = (
        35
        + 10 * math.sin(t / 6)
        + random.uniform(-2, 2)
    )

    return max(
        0,
        min(100, value)
    )


def generate_lane_keep_command(t):
    value = (
        2 * math.sin(t / 2)
        + random.uniform(-0.3, 0.3)
    )

    return max(
        -10,
        min(10, value)
    )


def generate_object_distance(t):
    value = (
        45
        + 8 * math.sin(t / 7)
        + random.uniform(-1, 1)
    )

    return max(
        2,
        min(100, value)
    )



def value_to_payload(signal_name, value):

    if signal_name == "vehicle_speed":

        encoded = int(value * 100)

    elif signal_name == "steering_angle":

        encoded = int(
            (value + 50) * 100
        )

    elif signal_name == "brake_pressure":

        encoded = int(value * 100)

    elif signal_name == "accelerator_position":

        encoded = int(value * 100)

    elif signal_name == "lane_keep_command":

        encoded = int(
            (value + 20) * 100
        )

    elif signal_name == "object_distance":

        encoded = int(value * 100)

    else:

        encoded = 0

    high = (
        encoded >> 8
    ) & 0xFF

    low = encoded & 0xFF


    return [
        high,
        low,
        0,
        0,
        0,
        0,
        0,
        0
    ]




def generate_signal_value(
    signal_name,
    timestamp
):

    if signal_name == "vehicle_speed":

        return generate_vehicle_speed(
            timestamp
        )

    elif signal_name == "steering_angle":

        return generate_steering_angle(
            timestamp
        )

    elif signal_name == "brake_pressure":

        return generate_brake_pressure(
            timestamp
        )

    elif signal_name == "accelerator_position":

        return generate_accelerator_position(
            timestamp
        )

    elif signal_name == "lane_keep_command":

        return generate_lane_keep_command(
            timestamp
        )

    elif signal_name == "object_distance":

        return generate_object_distance(
            timestamp
        )

    return 0




def generate_normal_traffic(
    output_file,
    duration=60,
    seed=42
):

    random.seed(seed)

    messages = []


    for can_id, config in CAN_CONFIG.items():

        timestamp = 0

        while timestamp < duration:

            jitter = random.uniform(
                -0.05,
                0.05
            )

            interval = (
                config["interval"]
                * (1 + jitter)
            )

            timestamp += interval

            signal_name = config["name"]

            signal_value = (
                generate_signal_value(
                    signal_name,
                    timestamp
                )
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
                len(payload),
                "benign",
                0
            ])


    messages.sort(
        key=lambda row: row[0]
    )


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
        f"autonomous vehicle CAN messages "
        f"-> {output_file}"
    )


if __name__ == "__main__":

    generate_normal_traffic(
        "canSim/logs/train_benign.csv",
        duration=60,
        seed=42
    )

    generate_normal_traffic(
        "canSim/logs/test_benign.csv",
        duration=60,
        seed=100
    )