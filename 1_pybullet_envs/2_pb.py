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
robotid = p.loadURDF("ur5robotiq85/ur5_robotiq_85.urdf", [1, 0, 0])
numJoints = p.getNumJoints(robotid)
print(' !!! robot numjoints: ', numJoints)


#boxId = p.loadURDF("r2d2.urdf",startPos, startOrientation)
#set the center of mass frame (loadURDF sets base link frame) startPos/Ornp.resetBasePositionAndOrientation(boxId, startPos, startOrientation)
for i in range (10000):
    p.stepSimulation()
    time.sleep(1./240.)

p.disconnect()
