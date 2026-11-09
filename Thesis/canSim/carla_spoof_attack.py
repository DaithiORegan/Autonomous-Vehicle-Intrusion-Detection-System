import pandas as pd
from pathlib import Path

INPUT_FILE = Path(
    r"C:\Users\gripx\Downloads\DaithiORegan_FYP_Code\canSim\logs\carla_telemetry.csv"
)

OUTPUT_FILE = Path(
    r"C:\Users\gripx\Downloads\DaithiORegan_FYP_Code\canSim\logs\carla_steering_spoof.csv"
)



TARGET_CAN_ID = "0x101"

ATTACK_START = 0.40
ATTACK_END = 0.65

SPOOF_VALUE = 0.85



df = pd.read_csv(
    INPUT_FILE
)

print("=" * 70)
print("CARLA STEERING SPOOF ATTACK")
print("=" * 70)

print(
    f"Loaded {len(df)} CAN-style messages"
)




df["attack_type"] = "benign"

df["label"] = 0




steering_indices = df[
    df["can_id"] == TARGET_CAN_ID
].index


number_steering = len(
    steering_indices
)

start_position = int(
    number_steering * ATTACK_START
)

end_position = int(
    number_steering * ATTACK_END
)

attack_indices = steering_indices[
    start_position:end_position
]



df.loc[
    attack_indices,
    "value"
] = SPOOF_VALUE

df.loc[
    attack_indices,
    "attack_type"
] = "steering_spoof"

df.loc[
    attack_indices,
    "label"
] = 1




OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


print()
print(
    f"Steering messages: "
    f"{number_steering}"
)

print(
    f"Spoofed messages: "
    f"{len(attack_indices)}"
)

print(
    f"Spoof value: "
    f"{SPOOF_VALUE}"
)

print(
    f"Saved -> "
    f"{OUTPUT_FILE}"
)

print("=" * 70)