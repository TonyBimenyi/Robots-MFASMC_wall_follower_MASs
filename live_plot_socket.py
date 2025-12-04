import matplotlib.pyplot as plt
import time
import os

DATA_FILE = "/tmp/webots_live_data.csv"
POLL_INTERVAL = 0.15
MAX_POINTS = 800
DESIRED_LEFT_DISTANCE = 100  # constant target distance

plt.ion()
fig, ax = plt.subplots(figsize=(8,4))
actual_line, = ax.plot([], [], label="Actual Left Distance")
desired_line, = ax.plot([], [], label="Desired Distance (100)", linestyle='--')
ax.set_xlabel("Time (s)")
ax.set_ylabel("Distance")
ax.set_title("Left Wall Distance: Actual vs Desired")
ax.legend()
ax.grid(True)

def read_file():
    if not os.path.exists(DATA_FILE):
        return [], []
    with open(DATA_FILE, "r") as f:
        lines = f.readlines()
    t_list, actual = [], []
    for line in lines[1:]:  # skip header
        parts = line.strip().split(",")
        if len(parts) >= 2:
            try:
                tt = float(parts[0])
                ll = float(parts[1])
                t_list.append(tt)
                actual.append(ll)
            except:
                pass
    # create a desired distance list (constant 100)
    desired = [DESIRED_LEFT_DISTANCE] * len(actual)
    return t_list, actual, desired

try:
    while True:
        t, actual, desired = read_file()
        if t:
            # keep only last MAX_POINTS points
            if len(t) > MAX_POINTS:
                t = t[-MAX_POINTS:]
                actual = actual[-MAX_POINTS:]
                desired = desired[-MAX_POINTS:]
            actual_line.set_xdata(t)
            actual_line.set_ydata(actual)
            desired_line.set_xdata(t)
            desired_line.set_ydata(desired)
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.001)
        time.sleep(POLL_INTERVAL)
except KeyboardInterrupt:
    print("Plotter stopped by user")
