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
MAX_POINTS = 14000

# --- Setup the live plot with 2 subplots ---
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Top subplot: Left distance
lines_left = {}
for robot_name in DATA_FILES:
    lines_left[robot_name], = ax1.plot([], [], label=f"{robot_name} Left Distance")
desired_line, = ax1.plot([], [], label="Reference Trajectory", linestyle='--', color='black')
ax1.set_ylabel("Left Wall Distance (cm)")
ax1.set_title("MFASMC Wall-Following: Actual vs Desired")
ax1.legend()
ax1.grid(True)

# Bottom subplot: Distributed error Xi
lines_xi = {}
for robot_name in DATA_FILES:
    lines_xi[robot_name], = ax2.plot([], [], label=f"{robot_name} Xi")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Distributed Error Xi")
ax2.set_title("MFASMC Distributed Error Xi")
ax2.legend()
ax2.grid(True)

# --- Function to read CSV data ---
def read_csv(file_path):
    if not os.path.exists(file_path):
        return [], [], [], []
    t_list, left_list, xi_list, desired_list = [], [], [], []
    with open(file_path, "r") as f:
        lines_csv = f.readlines()
    for line in lines_csv[1:]:  # skip header
        parts = line.strip().split(",")
        if len(parts) >= 6:
            try:
                t_list.append(float(parts[0]))
                left_list.append(float(parts[1]))
                xi_list.append(float(parts[4]))       # Xi column
                desired_list.append(float(parts[5]))  # desired column
            except:
                pass
    return t_list, left_list, xi_list, desired_list

# --- Live plotting loop ---
try:
    while True:
        max_len = 0
        data_left_dict = {}
        data_xi_dict = {}
        desired_data = []

        # Read data for each robot
        for robot_name, file_path in DATA_FILES.items():
            t, left, xi, desired = read_csv(file_path)
            if len(t) > MAX_POINTS:
                t = t[-MAX_POINTS:]
                left = left[-MAX_POINTS:]
                xi = xi[-MAX_POINTS:]
                desired = desired[-MAX_POINTS:]
            data_left_dict[robot_name] = (t, left)
            data_xi_dict[robot_name] = (t, xi)
            max_len = max(max_len, len(t))
            if desired:
                desired_data = desired  # assume all robots track same trajectory

        # Update left distance subplot
        for robot_name, (t, left) in data_left_dict.items():
            lines_left[robot_name].set_xdata(t)
            lines_left[robot_name].set_ydata(left)
        if max_len > 0 and desired_data:
            any_t = next(iter(data_left_dict.values()))[0]
            desired_line.set_xdata(any_t)
            desired_line.set_ydata(desired_data)

        # Update Xi subplot
        for robot_name, (t, xi) in data_xi_dict.items():
            lines_xi[robot_name].set_xdata(t)
            lines_xi[robot_name].set_ydata(xi)

        ax1.relim(); ax1.autoscale_view()
        ax2.relim(); ax2.autoscale_view()
        plt.pause(0.001)
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    print("Live plot stopped by user")
