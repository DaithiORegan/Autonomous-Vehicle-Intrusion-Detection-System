import ast
from collections import deque, defaultdict

import numpy as np
import pandas as pd


def parse_payload(value):

    if isinstance(value, list):
        return value

    try:
        return ast.literal_eval(value)

    except (ValueError, SyntaxError):
        return [0] * 8


def compute_features(dataset):

    df = dataset.copy()

    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    # -----------------------------------------------------
    # BASIC CAN FEATURES
    # -----------------------------------------------------

    df["can_id_int"] = df["can_id"].apply(
        lambda value: int(str(value), 16)
    )

    payloads = df["data"].apply(
        parse_payload
    )

    df["payload_mean"] = payloads.apply(
        np.mean
    )

    df["payload_std"] = payloads.apply(
        np.std
    )

    df["payload_min"] = payloads.apply(
        np.min
    )

    df["payload_max"] = payloads.apply(
        np.max
    )

    df["global_inter_time"] = (
        df["timestamp"]
        .diff()
        .fillna(0)
    )

    df["id_inter_time"] = (
        df.groupby("can_id")["timestamp"]
        .diff()
        .fillna(0)
    )

    # -----------------------------------------------------
    # BUS RATE
    # -----------------------------------------------------

    bus_window = deque()

    bus_rates = []

    for timestamp in df["timestamp"]:

        bus_window.append(timestamp)

        while (
            bus_window
            and timestamp - bus_window[0] > 1
        ):
            bus_window.popleft()

        bus_rates.append(
            len(bus_window)
        )

    df["bus_rate_1s"] = bus_rates

    # -----------------------------------------------------
    # PER-ID RATE
    # -----------------------------------------------------

    id_windows = defaultdict(deque)

    id_rates = []

    for _, row in df.iterrows():

        can_id = row["can_id"]
        timestamp = row["timestamp"]

        window = id_windows[can_id]

        window.append(timestamp)

        while (
            window
            and timestamp - window[0] > 1
        ):
            window.popleft()

        id_rates.append(
            len(window)
        )

    df["id_rate_1s"] = id_rates

    # -----------------------------------------------------
    # PAYLOAD CHANGE
    # -----------------------------------------------------

    previous_payload = {}

    payload_change = []

    for _, row in df.iterrows():

        can_id = row["can_id"]

        payload = np.array(
            parse_payload(row["data"]),
            dtype=float
        )

        if can_id not in previous_payload:

            change = 0

        else:

            change = np.mean(
                np.abs(
                    payload
                    - previous_payload[can_id]
                )
            )

        payload_change.append(
            change
        )

        previous_payload[can_id] = payload

    df["payload_change"] = payload_change

    # -----------------------------------------------------
    # SIGNAL-SPECIFIC TEMPORAL FEATURES
    # -----------------------------------------------------

    df["signal_delta"] = (
        df.groupby("signal_name")["signal_value"]
        .diff()
        .fillna(0)
    )

    df["signal_time_delta"] = (
        df.groupby("signal_name")["timestamp"]
        .diff()
        .fillna(0)
    )

    df["signal_rate_of_change"] = 0.0

    valid_time = (
        df["signal_time_delta"] > 0
    )

    df.loc[
        valid_time,
        "signal_rate_of_change"
    ] = (
        df.loc[
            valid_time,
            "signal_delta"
        ]
        /
        df.loc[
            valid_time,
            "signal_time_delta"
        ]
    )

    # -----------------------------------------------------
    # BUILD CURRENT VEHICLE STATE
    # -----------------------------------------------------

    vehicle_state = {
        "vehicle_speed": 0.0,
        "steering_angle": 0.0,
        "brake_pressure": 0.0,
        "accelerator_position": 0.0,
        "lane_keep_command": 0.0,
        "object_distance": 50.0
    }

    speed_context = []
    steering_context = []
    brake_context = []
    accelerator_context = []
    lane_context = []
    distance_context = []

    for _, row in df.iterrows():

        signal = row["signal_name"]

        try:
            value = float(
                row["signal_value"]
            )
        except:
            value = 0.0

        if signal in vehicle_state:
            vehicle_state[signal] = value

        speed_context.append(
            vehicle_state[
                "vehicle_speed"
            ]
        )

        steering_context.append(
            vehicle_state[
                "steering_angle"
            ]
        )

        brake_context.append(
            vehicle_state[
                "brake_pressure"
            ]
        )

        accelerator_context.append(
            vehicle_state[
                "accelerator_position"
            ]
        )

        lane_context.append(
            vehicle_state[
                "lane_keep_command"
            ]
        )

        distance_context.append(
            vehicle_state[
                "object_distance"
            ]
        )

    df["ctx_speed"] = speed_context
    df["ctx_steering"] = steering_context
    df["ctx_brake"] = brake_context
    df["ctx_accelerator"] = accelerator_context
    df["ctx_lane_keep"] = lane_context
    df["ctx_object_distance"] = distance_context

    # -----------------------------------------------------
    # CROSS-SIGNAL CONTEXT FEATURES
    # -----------------------------------------------------

    # Large steering input becomes more significant
    # as vehicle speed increases.
    df["speed_steering_context"] = (
        np.abs(
            df["ctx_steering"]
        )
        *
        df["ctx_speed"]
    )

    # Compare requested lane correction against actual
    # steering behaviour.
    df["lane_steering_difference"] = (
        np.abs(
            df["ctx_steering"]
            -
            df["ctx_lane_keep"]
        )
    )

    # Brake and accelerator pressed simultaneously.
    df["brake_accel_overlap"] = (
        (
            df["ctx_brake"] / 100
        )
        *
        (
            df["ctx_accelerator"] / 100
        )
    )

    # High speed combined with short object distance.
    df["speed_distance_risk"] = (
        df["ctx_speed"]
        /
        (
            df["ctx_object_distance"] + 1
        )
    )

    return df


FEATURE_COLUMNS = [
    "can_id_int",
    "dlc",

    "global_inter_time",
    "id_inter_time",
    "bus_rate_1s",
    "id_rate_1s",

    "payload_mean",
    "payload_std",
    "payload_min",
    "payload_max",
    "payload_change",

    "signal_delta",
    "signal_rate_of_change",

    "ctx_speed",
    "ctx_steering",
    "ctx_brake",
    "ctx_accelerator",
    "ctx_lane_keep",
    "ctx_object_distance",

    "speed_steering_context",
    "lane_steering_difference",
    "brake_accel_overlap",
    "speed_distance_risk"
]