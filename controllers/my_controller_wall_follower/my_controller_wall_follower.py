from controller import Robot, Motor, DistanceSensor, Camera
import time, os
import math

# --- MFASMC parameters ---
RHO = 1.45
LAMBDA = 0.2
OMEGA = 0.35
SIGMA = 0.15
GAMMA = 0.4
ALPHA = 1.0
TAU_S = 0.0005
PI = 3.1415926

# --- Robot topology ---
NEIGHBORS = {
    "robot1": ["robot2"],
    "robot2": ["robot1", "robot3"],
    "robot3": ["robot2"]
}

# --- Time-varying desired trajectory ---
def desired_trajectory(t):
    """Time-varying left wall distance (cm). Example: sinusoidal around 300cm."""
    # return 300 + 47 * math.sin(0.09 * math.pi * t) + 50 * math.cos(0.07 * math.pi * t)

    return 310 + 40 * math.sin(0.08 * math.pi * t + 0.5) + 45 * math.cos(0.06 * math.pi * t - 0.3)
    # return 300 + 50 * math.sin((1.2 + 0.3 * math.sin(0.05 * t)) * t)
    # return 0.6*sin(0.07*PI*t) + 0.7*cos(0.04*PI*t)





# --- Formation (distributed) errors ---
def distributed_error_1(Y1, TargetVelocity1, Y_neighbors):
    Xi1 = 0.901 * TargetVelocity1 - Y1 + 35
    return Xi1

def distributed_error_2(Y2, TargetVelocity1, Y_neighbors):
    Xi2 = 1.07 * TargetVelocity1 - Y2 - 15 
    return Xi2

def distributed_error_3(Y3, TargetVelocity1, Y_neighbors):
    Xi3 = 1.15 * TargetVelocity1 - Y3 - 44 
    return Xi3

# --- MFASMC controllers ---
def mfasmc_controller_1(Y1, Y_neighbors, u_prev, Xi_prev, Delta_Y_neighbors, TargetVelocity):
    Xi = distributed_error_1(Y1, TargetVelocity, Y_neighbors)
    s = ALPHA * Xi - Xi_prev
    delta_u_MFAC = (RHO * 1.0 / (LAMBDA + 1.0**2)) * Xi
    sum_delta_yj = sum(Delta_Y_neighbors)
    delta_u_SMC = (OMEGA * 1.0 / (SIGMA + 1.0**2)) * (
        (Xi + sum_delta_yj) / max(1, len(Delta_Y_neighbors)) - Xi / max(1, len(Delta_Y_neighbors)) + TAU_S * math.copysign(1, s)
    )
    u = u_prev + delta_u_MFAC + GAMMA * delta_u_SMC
    return u, Xi

def mfasmc_controller_2(Y2, Y_neighbors, u_prev, Xi_prev, Delta_Y_neighbors, TargetVelocity):
    Xi = distributed_error_2(Y2, TargetVelocity, Y_neighbors)
    s = ALPHA * Xi - Xi_prev
    delta_u_MFAC = (RHO * 1.0 / (LAMBDA + 1.0**2)) * Xi
    sum_delta_yj = sum(Delta_Y_neighbors)
    delta_u_SMC = (OMEGA * 1.0 / (SIGMA + 1.0**2)) * (
        (Xi + sum_delta_yj) / max(1, len(Delta_Y_neighbors)) - Xi / max(1, len(Delta_Y_neighbors)) + TAU_S * math.copysign(1, s)
    )
    u = u_prev + delta_u_MFAC + GAMMA * delta_u_SMC
    return u, Xi

def mfasmc_controller_3(Y3, Y_neighbors, u_prev, Xi_prev, Delta_Y_neighbors, TargetVelocity):
    Xi = distributed_error_3(Y3, TargetVelocity, Y_neighbors)
    s = ALPHA * Xi - Xi_prev
    delta_u_MFAC = (RHO * 1.0 / (LAMBDA + 1.0**2)) * Xi
    sum_delta_yj = sum(Delta_Y_neighbors)
    delta_u_SMC = (OMEGA * 1.0 / (SIGMA + 1.0**2)) * (
        (Xi + sum_delta_yj) / max(1, len(Delta_Y_neighbors)) - Xi / max(1, len(Delta_Y_neighbors)) + TAU_S * math.copysign(1, s)
    )
    u = u_prev + delta_u_MFAC + GAMMA * delta_u_SMC
    return u, Xi

# --- Mapping Webots names to robot logic ---
ROBOT_NAME_MAP = {
    "e-puck": "robot1",
    "e-puck(1)": "robot2",
    "e-puck(2)": "robot3"
}

MFASMC_CONTROLLERS = {
    "robot1": mfasmc_controller_1,
    "robot2": mfasmc_controller_2,
    "robot3": mfasmc_controller_3
}

# --- Run robot ---
def run_robot(robot):
    timestep = int(robot.getBasicTimeStep())
    max_speed = 3.28

    webots_name = robot.getName()
    robot_name = ROBOT_NAME_MAP.get(webots_name, "robot1")
    controller_func = MFASMC_CONTROLLERS[robot_name]

    # MFASMC states
    u_prev = 0.0
    Xi_prev = 0.0
    Delta_Y_neighbors = [0.0 for _ in NEIGHBORS[robot_name]]

    # Motors
    left_motor = robot.getDevice("left wheel motor")
    right_motor = robot.getDevice("right wheel motor")
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)

    # Sensors
    prox_sensors = []
    for ind in range(8):
        sensor = robot.getDevice(f"ps{ind}")
        sensor.enable(timestep)
        prox_sensors.append(sensor)

    # Camera
    camera = robot.getDevice("camera")
    camera.enable(timestep)
    cam_width = camera.getWidth()
    cam_height = camera.getHeight()

    # CSV logging
    data_file = f"/tmp/{robot_name}_mfasmc_data.csv"
    try: os.remove(data_file)
    except: pass
    with open(data_file, "w") as f:
        f.write("time,left,front,u,Xi,desired\n")

    start_time = time.time()
    last_time = time.time()

    while robot.step(timestep) != -1:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # --- Get left and front distances ---
        left_distance = (prox_sensors[5].getValue() + prox_sensors[6].getValue()) / 2.0
        front_distance = prox_sensors[7].getValue()

        # --- Time-varying desired ---
        TargetVelocity = desired_trajectory(current_time - start_time)

        # --- Read neighbor distances (placeholder) ---
        y_neighbors = [left_distance for _ in NEIGHBORS[robot_name]]

        # --- MFASMC control ---
        u, Xi = controller_func(left_distance, y_neighbors, u_prev, Xi_prev, Delta_Y_neighbors, TargetVelocity)
        u = max(-1.5, min(1.5, u))
        delta_u = u - u_prev
        u_prev = u
        Xi_prev = Xi
        Delta_Y_neighbors = [delta_u for _ in NEIGHBORS[robot_name]]

        # --- Wall-following logic ---
        left_wall = left_distance > 80
        front_wall = front_distance > 80

        if front_wall:
            left_motor.setVelocity(max_speed)
            right_motor.setVelocity(-max_speed * 0.1)
        elif left_wall:
            left_speed = max_speed - u
            right_speed = max_speed + u
            left_motor.setVelocity(max(-max_speed, min(max_speed, left_speed)))
            right_motor.setVelocity(max(-max_speed, min(max_speed, right_speed)))
        else:
            left_motor.setVelocity(max_speed / 8)
            right_motor.setVelocity(max_speed)

        # Camera read (optional)
        image = camera.getImage()
        center_r = camera.imageGetRed(image, cam_width, cam_width//2, cam_height//2)
        center_g = camera.imageGetGreen(image, cam_width, cam_width//2, cam_height//2)
        center_b = camera.imageGetBlue(image, cam_width, cam_width//2, cam_height//2)
        print(f"{robot_name} | Center RGB: ({center_r},{center_g},{center_b})")

        # CSV logging
        with open(data_file, "a") as f:
            t = current_time - start_time
            f.write(f"{t:.3f},{left_distance:.6f},{front_distance:.6f},{u:.6f},{Xi:.6f},{TargetVelocity:.6f}\n")

        print(f"{robot_name} | Left: {left_distance:.2f}, Front: {front_distance:.2f}, u: {u:.3f}, Xi: {Xi:.3f}, Desired: {TargetVelocity:.2f}")

if __name__ == "__main__":
    my_robot = Robot()
    run_robot(my_robot)