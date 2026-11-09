import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

FILE = r"canSim\logs\carla_validation\carla_signal_ids_results.csv"

df = pd.read_csv(FILE)

x = np.arange(len(df))
width = 0.25

plt.figure(figsize=(9, 5.5))

plt.bar(
    x - width,
    df["precision"],
    width,
    label="Precision"
)

plt.bar(
    x,
    df["recall"],
    width,
    label="Recall"
)

plt.bar(
    x + width,
    df["f1"],
    width,
    label="F1-score"
)

plt.xticks(
    x,
    [attack.capitalize() for attack in df["attack"]]
)

plt.xlabel("Attack Type")
plt.ylabel("Score")
plt.title("CARLA Signal-Aware IDS Performance")
plt.ylim(0, 1.05)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.35
)

plt.legend()
plt.tight_layout()

plt.savefig(
    r"canSim\logs\carla_validation\carla_ids_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()