import matplotlib.pyplot as plt
import numpy as np

attacks = ["DoS", "Spoof", "Replay"]

statistical_f1 = [
    0.780823,
    0.417495,
    0.583609
]

isolation_forest_f1 = [
    0.920641,
    0.038095,
    0.068687
]

x = np.arange(len(attacks))
width = 0.35

plt.figure(figsize=(9, 5.5))

plt.bar(
    x - width / 2,
    statistical_f1,
    width,
    label="Statistical IDS"
)

plt.bar(
    x + width / 2,
    isolation_forest_f1,
    width,
    label="Isolation Forest"
)

plt.xlabel("Attack Type")
plt.ylabel("F1-score")
plt.title("Controlled CAN IDS Performance by Attack Type")

plt.xticks(x, attacks)
plt.ylim(0, 1.0)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.legend()
plt.tight_layout()

plt.show()