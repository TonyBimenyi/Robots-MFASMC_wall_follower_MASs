import matplotlib.pyplot as plt
import time
import os
import math

# Paths to each robot's CSV file (from your MFASMC code)
DATA_FILES = {
    "robot1": "/tmp/robot1_mfasmc_data.csv",
    "robot2": "/tmp/robot2_mfasmc_data.csv",
    "robot3": "/tmp/robot3_mfasmc_data.csv"
}

POLL_INTERVAL = 0.15  # seconds
MAX_POINTS = 800

# --- Setup the live plot ---
plt.ion()
fig, ax = plt.subplots(figsize=(10, 5))
lines = {}
for robot_name in DATA_FILES:
    lines[robot_name], = ax.plot([], [], label=f"{robot_name} Left Distance")
# Reference trajectory line
desired_line, = ax.plot([], [], label="Reference Trajectory", linestyle='--', color='black')

ax.set_xlabel("Time (s)")
ax.set_ylabel("Left Wall Distance (cm)")
ax.set_title("MFASMC Wall-Following: Actual vs Time-Varying Reference")
ax.legend()
ax.grid(True)

# --- Function to read CSV data ---
def read_csv(file_path):
    if not os.path.exists(file_path):
        return [], [], []
    t_list, left_list, desired_list = [], [], []
    with open(file_path, "r") as f:
        lines_csv = f.readlines()
    for line in lines_csv[1:]:  # skip header
        parts = line.strip().split(",")
        if len(parts) >= 6:
            try:
                t_list.append(float(parts[0]))
                left_list.append(float(parts[1]))
                desired_list.append(float(parts[5]))  # 'desired' column
            except:
                pass
    return t_list, left_list, desired_list

# --- Live plotting loop ---
try:
    while True:
        max_len = 0
        # Read data for each robot
        data_dict = {}
        desired_data = []
        for robot_name, file_path in DATA_FILES.items():
            t, left, desired = read_csv(file_path)
            if len(t) > MAX_POINTS:
                t = t[-MAX_POINTS:]
                left = left[-MAX_POINTS:]
                desired = desired[-MAX_POINTS:]
            data_dict[robot_name] = (t, left)
            max_len = max(max_len, len(t))
            if desired:
                desired_data = desired  # assume all robots track same trajectory

        # Update robot lines
        for robot_name, (t, left) in data_dict.items():
            lines[robot_name].set_xdata(t)
            lines[robot_name].set_ydata(left)

        # Update reference trajectory line
        if max_len > 0 and desired_data:
            any_t = next(iter(data_dict.values()))[0]  # use any robot's time
            desired_line.set_xdata(any_t)
            desired_line.set_ydata(desired_data)

        ax.relim()
        ax.autoscale_view()
        plt.pause(0.001)
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("Live plot stopped by user")