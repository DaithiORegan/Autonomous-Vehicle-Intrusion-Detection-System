import pandas as pd
import matplotlib.pyplot as plt

BENIGN_FILE = r"canSim\logs\carla_telemetry.csv"
DOS_FILE = r"canSim\logs\carla_validation\carla_dos.csv"

benign = pd.read_csv(BENIGN_FILE)
dos = pd.read_csv(DOS_FILE)

benign["timestamp"] = pd.to_numeric(benign["timestamp"], errors="coerce")
dos["timestamp"] = pd.to_numeric(dos["timestamp"], errors="coerce")

benign = benign.dropna(subset=["timestamp"]).sort_values("timestamp")
dos = dos.dropna(subset=["timestamp"]).sort_values("timestamp")

# Calculate inter-message intervals
benign["inter_time"] = benign["timestamp"].diff()
dos["inter_time"] = dos["timestamp"].diff()

# Remove first NaN
benign_intervals = benign["inter_time"].dropna()
dos_intervals = dos["inter_time"].dropna()

plt.figure(figsize=(10, 5.5))

plt.plot(
    benign_intervals.reset_index(drop=True),
    benign_intervals.values,
    label="Benign Traffic",
    linewidth=1.2
)

plt.plot(
    dos_intervals.reset_index(drop=True),
    dos_intervals.values,
    label="DoS Traffic",
    linewidth=1.2
)

plt.xlabel("Message Sequence")
plt.ylabel("Inter-Message Interval (s)")
plt.title("CAN Inter-Message Timing: Benign vs DoS Traffic")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.show()