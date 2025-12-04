"""my_controller_wall_follower controller with PID + CSV logging."""

from controller import Robot, Motor, DistanceSensor
import time
import os

def run_robot(robot):
    """Wall following controller"""

    timestep = int(robot.getBasicTimeStep())
    max_speed = 3.28

    Kp = 0.02   # stronger proportional
    Ki = 0.00001
    Kd = 0.005  # slightly stronger derivative
    
    
    error_sum = 0
    last_error = 0
    last_time = time.time()

    # Motors
    left_motor = robot.getDevice("left wheel motor")
    right_motor = robot.getDevice("right wheel motor")

    left_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)

    right_motor.setPosition(float('inf'))
    right_motor.setVelocity(0.0)

    # Sensors ps0–ps7
    prox_sensors = []
    for ind in range(8):
        sensor = robot.getDevice(f"ps{ind}")
        sensor.enable(timestep)
        prox_sensors.append(sensor)

    desired_left_distance = 100  # You can adjust this target distance

    # --- CSV file for live plotting ---
    data_file = "/tmp/webots_live_data.csv"
    # remove old file at start
    try:
        os.remove(data_file)
    except Exception:
        pass
    # write header
    with open(data_file, "w") as f:
        f.write("time,left,front\n")

    start_time = time.time()

    # Main loop
    while robot.step(timestep) != -1:

        # Read LEFT side sensors
        left_distance = (prox_sensors[5].getValue() + prox_sensors[6].getValue()) / 2.0

        # Read FRONT sensor
        front_distance = prox_sensors[7].getValue()

        # Print distances
        print("Left distance:", left_distance, " | Front distance:", front_distance)

        # --- WRITE TO CSV ---
        try:
            with open(data_file, "a") as f:
                t = time.time() - start_time
                f.write(f"{t:.3f},{left_distance:.6f},{front_distance:.6f}\n")
                f.flush()
        except Exception as e:
            print("Warning: failed to write data file:", e)

        # Threshold logic
        left_wall = left_distance > 80
        front_wall = front_distance > 80

        # -----------------------
        # PID COMPUTATION
        # -----------------------
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        error = desired_left_distance - left_distance
        error_sum += error * dt
        d_error = (error - last_error) / dt if dt > 0 else 0
        last_error = error

        pid_output = Kp * error + Ki * error_sum + Kd * d_error
        pid_output = max(-1.5, min(1.5, pid_output))
        # -----------------------

        # Wall following actions
        if front_wall:  # Too close to front wall → turn right
            print('Turn right in place')
            left_motor.setVelocity(max_speed)
            right_motor.setVelocity(-max_speed * 0.3)

        elif left_wall:  # Wall on the left → follow it straight with PID steering
            print('Drive Forward (PID steering)')
            
            left_speed = max_speed - pid_output
            right_speed = max_speed + pid_output

            # limit speed
            left_speed = max(-max_speed, min(max_speed, left_speed))
            right_speed = max(-max_speed, min(max_speed, right_speed))

            left_motor.setVelocity(left_speed)
            right_motor.setVelocity(right_speed)

        else:  # No wall → turn left to find it
            print('Turn left')
            left_motor.setVelocity(max_speed/8)
            right_motor.setVelocity(max_speed)

if __name__ == "__main__":
    my_robot = Robot()
    run_robot(my_robot)
