import pybullet
import numpy as np
import threading
import time


class EyesCamera:
    """Gripper handling for Robotiq 2F85."""

    def __init__(self, robot, tool):
        self.robot = robot
        self.tool = tool
        #pos = [0.1339999999999999, -0.49199999999872496, 0.5]
        pos = [0, -1, 0]
        #pos = [0.1339999999999999, -1, 0.5]
        rot = pybullet.getQuaternionFromEuler([np.pi, 0, np.pi])
        urdf = "../onrobot_camera/onrobot_eyes.urdf"
        self.camera = pybullet.loadURDF(urdf, pos)
        self.n_joints = pybullet.getNumJoints(self.camera)

        # Connect gripper base to robot tool.
        #pybullet.createConstraint(self.robot, tool, self.onrobot_camera, 0, jointType=pybullet.JOINT_FIXED, jointAxis=[0, 0, 0],
        #                          parentFramePosition=[0, 0, 0], childFramePosition=[0, 0, -0.07],
        #                          childFrameOrientation=pybullet.getQuaternionFromEuler([0, 0, np.pi / 2]))



    # Control joint positions by enforcing hard contraints on gripper behavior.
    # Set one joint as the open/close motor joint (other joints should mimic).
    def step(self):
        while True:
            try:
                currj = [pybullet.getJointState(self.body, i)[0] for i in range(self.n_joints)]
                indj = [6, 3, 8, 5, 10]
                targj = [currj[1], -currj[1], -currj[1], currj[1], currj[1]]
                pybullet.setJointMotorControlArray(self.body, indj, pybullet.POSITION_CONTROL, targj,
                                                   positionGains=np.ones(5))
            except:
                return
            time.sleep(0.001)

    # Close gripper fingers.
    def activate(self):
        pybullet.setJointMotorControl2(self.body, self.motor_joint, pybullet.VELOCITY_CONTROL, targetVelocity=1,
                                       force=10)
        self.activated = True

    # Open gripper fingers.
    def release(self):
        pybullet.setJointMotorControl2(self.body, self.motor_joint, pybullet.VELOCITY_CONTROL, targetVelocity=-1,
                                       force=10)
        self.activated = False
