import pandas as pd
import matplotlib.pyplot as plt

BENIGN_FILE = r"canSim\logs\carla_telemetry.csv"
DOS_FILE = r"canSim\logs\carla_validation\carla_dos.csv"

benign = pd.read_csv(BENIGN_FILE)
dos = pd.read_csv(DOS_FILE)

benign["timestamp"] = pd.to_numeric(benign["timestamp"], errors="coerce")
dos["timestamp"] = pd.to_numeric(dos["timestamp"], errors="coerce")

benign = benign.dropna(subset=["timestamp"])
dos = dos.dropna(subset=["timestamp"])

# Convert to elapsed seconds
benign["elapsed"] = benign["timestamp"] - benign["timestamp"].min()
dos["elapsed"] = dos["timestamp"] - dos["timestamp"].min()

# Count messages in 1-second bins
benign["second"] = benign["elapsed"].astype(int)
dos["second"] = dos["elapsed"].astype(int)

benign_rate = benign.groupby("second").size()
dos_rate = dos.groupby("second").size()

plt.figure(figsize=(10, 5.5))

plt.plot(
    benign_rate.index,
    benign_rate.values,
    label="Benign Traffic",
    linewidth=1.5
)

plt.plot(
    dos_rate.index,
    dos_rate.values,
    label="DoS Traffic",
    linewidth=1.5
)

plt.xlabel("Elapsed Time (s)")
plt.ylabel("Messages per Second")
plt.title("CAN Message Rate: Benign vs DoS Traffic")
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()

plt.show()