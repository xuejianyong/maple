import numpy as np
import robosuite as suite
from robosuite.controllers import load_controller_config
from robosuite.utils.input_utils import *
from robosuite.robots import Bimanual


options = {}
options["env_name"] = "PickPlace"
options["robots"] = 'UR5e'
options["controller_configs"] = "IK_POSE"


joint_dim = 6 if options["robots"] == "UR5e" else 7
controller_name = "OSC_POSE"
options["controller_configs"] = suite.load_controller_config(default_controller=controller_name)
controller_settings = {
        "OSC_POSE":         [6, 6, 0.1],
        "OSC_POSITION":     [3, 3, 0.1],
        "IK_POSE":          [6, 6, 0.01],
        "JOINT_POSITION":   [joint_dim, joint_dim, 0.2],
        "JOINT_VELOCITY":   [joint_dim, joint_dim, -0.1],
        "JOINT_TORQUE":     [joint_dim, joint_dim, 0.25]
    }

print('controller settings:', controller_settings[controller_name])
action_dim = controller_settings[controller_name][0]
num_test_steps = controller_settings[controller_name][1]
test_value = controller_settings[controller_name][2]

# Define the number of timesteps to use per controller action as well as timesteps in between actions
steps_per_action = 75
steps_per_rest = 75

# Help message to user
print()
print("Press \"H\" to show the viewer control panel.")

# initialize the task
env = suite.make(
    **options,
    has_renderer=True,
    has_offscreen_renderer=False,
    ignore_done=True,
    use_camera_obs=False,
    horizon=(steps_per_action + steps_per_rest) * num_test_steps,
    control_freq=20,
)

env.reset()
env.viewer.set_camera(camera_id=0)

# To accommodate for multi-arm settings (e.g.: Baxter), we need to make sure to fill any extra action space
# Get total number of arms being controlled
n = 0
gripper_dim = 0
for robot in env.robots:
    gripper_dim = robot.gripper["right"].dof if isinstance(robot, Bimanual) else robot.gripper.dof
    n += int(robot.action_dim / (action_dim + gripper_dim))

# Define neutral value
neutral = np.zeros(action_dim + gripper_dim)

# Keep track of done variable to know when to break loop
count = 0
# Loop through controller space
while count < num_test_steps:
    print('-------------------------------------------------')
    action = neutral.copy()
    print('count:', count, 'action: ', action, ' test_value: ', test_value)

    for i in range(steps_per_action):
        if controller_name in {'IK_POSE', 'OSC_POSE'} and count > 2:
            # Set this value to be the scaled axis angle vector
            vec = np.zeros(3)
            vec[count - 3] = test_value
            action[3:6] = vec
            print('vec: ', vec, ' action: ', action)
        else:
            action[count] = test_value
        total_action = np.tile(action, n)
        env.step(total_action)
        env.render()
    for i in range(steps_per_rest):
        total_action = np.tile(neutral, n)
        env.step(total_action)
        env.render()
    count += 1

# Shut down this env before starting the next test
env.close()
