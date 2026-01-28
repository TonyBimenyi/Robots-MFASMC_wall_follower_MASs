# Distributed MFASMC Wall-Following Robots in Webots

This repository contains the implementation of **Model-Free Adaptive Sliding Mode Control (MFASMC)** for a team of e-puck robots in Webots. The robots perform **wall-following behavior** while maintaining a **formation** using distributed multi-agent control strategies.  

## Key Features

- **Distributed Formation Control**: Each robot computes its local formation error (`ξ_i`) based on its own sensor readings and relative distances to neighboring robots.  
- **MFASMC Controller**: Combines **Model-Free Adaptive Control (MFAC)** and **Sliding Mode Control (SMC)** to ensure robustness, real-time adaptability, and specified performance for each robot.  
- **Consensus-based Control**: Robots share virtual “neighbor updates” to maintain formation and achieve cooperative behavior.  
- **Wall-Following Behavior**: Uses e-puck proximity sensors (`ps0–ps7`) to detect walls and obstacles.  
- **Camera Integration**: Demonstrates reading and logging camera data for further analysis.  
- **CSV Logging**: Records formation error and control signals for each robot for offline analysis.  

## Controller Overview

- **Distributed Error Function (`distributed_error_X`)**: Computes each robot's formation error as a combination of:
  - Local tracking error (distance to wall or target trajectory)  
  - Consensus error (difference between robot and neighbors)
  

Where:  
- **MFAC**: Adaptive term based on the current error `ξ_i`.  
- **SMC**: Sliding mode term ensuring robustness and formation maintenance.  
- **Sliding Surface**: \( s_i(k) = \alpha \xi_i(k) - \xi_i(k-1) \)  

## Topology

- **Robot 1** (`e-puck`): neighbor → Robot 2  
- **Robot 2** (`e-puck(1)`): neighbors → Robot 1, Robot 3  
- **Robot 3** (`e-puck(2)`): neighbor → Robot 2  

This neighbor topology is used for the consensus term in distributed control.  

## Usage

1. Open the project in **Webots**.  
2. Load the `my_controller_wall_follower.py` controller for each robot.  
3. Run the simulation — each robot will compute its MFASMC control in real-time.  
4. Check `/tmp/` for CSV logs: `robot1_mfasmc_data.csv`, etc.  

## Dependencies

- Webots (robot simulator)  
- Python 3.x  
- Standard Python libraries: `time`, `os`, `math`  

---

## License

This project is licensed under the MIT License.  

---

**Short Description for GitHub page:**  
> Real-time distributed formation control of e-puck robots using Model-Free Adaptive Sliding Mode Control (MFASMC) in Webots.  