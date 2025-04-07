from collections import namedtuple

import pybullet as p
import time
import pybullet_data
import numpy as np
physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0,0,-10)
planeId = p.loadURDF("plane.urdf")

startPos = [1,1,1]
startOrientation = p.getQuaternionFromEuler([0,0,0])
#bikeid = p.loadURDF("./bicycle/bike.urdf", startPos, startOrientation)
robotid = p.loadURDF("./ur5e/ur5_robotiq_85.urdf", [1,0,0])
numJoints = p.getNumJoints(robotid)
print(' !!! robot numjoints: ', numJoints)

pos = [0.1339999999999999, -0.49199999999872496, 0.5]
rot = p.getQuaternionFromEuler([np.pi, 0, np.pi])
robotiq_gripper_simple = p.loadURDF("./robotiq_2f_85/robotiq_2f_85.urdf", pos, rot)
# p.createConstraint(robotid, 9, robotiq_gripper_simple, 0 , jointType=pybullet.JOINT_FIXED, jointAxis=[0, 0, 0], parentFramePosition=[0, 0, 0], childFramePosition=[0, 0, -0.07], childFrameOrientation=pybullet.getQuaternionFromEuler([0, 0, np.pi / 2]))
grippernumJoints = p.getNumJoints(robotiq_gripper_simple)
print('gripper numjoints: ', grippernumJoints)

#boxId = p.loadURDF("r2d2.urdf",startPos, startOrientation)
#set the center of mass frame (loadURDF sets base link frame) startPos/Ornp.resetBasePositionAndOrientation(boxId, startPos, startOrientation)
for i in range (10000):
    p.stepSimulation()
    time.sleep(1./240.)
cubePos, cubeOrn = p.getBasePositionAndOrientation(bikeid)
print(cubePos,cubeOrn)
p.disconnect()
