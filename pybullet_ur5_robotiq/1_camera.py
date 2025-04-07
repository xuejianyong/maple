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
bikeid = p.loadURDF("./bicycle/bike.urdf", startPos, startOrientation)

width = 320
height = 320
aspect = 1
cam_pos = (0, 0, 0)
cam_tar = (1, 1, 1)
cam_up_vector = (0, 0, 1)
near = 0.1
far = 5
size = (320, 320)
fov = 40
view_matrix = p.computeViewMatrix(cam_pos, cam_tar, cam_up_vector)
projection_matrix = p.computeProjectionMatrixFOV(fov, aspect, near, far)
p.getCameraImage(width, height,view_matrix, projection_matrix,)
#p.getDebugVisualizerCamera( cameraDistance=3, cameraYaw=30, cameraPitch=52, cameraTargetPosition=[0,0,0])


#boxId = p.loadURDF("r2d2.urdf",startPos, startOrientation)
#set the center of mass frame (loadURDF sets base link frame) startPos/Ornp.resetBasePositionAndOrientation(boxId, startPos, startOrientation)
for i in range (20000):
    p.stepSimulation()
    time.sleep(1./240.)
cubePos, cubeOrn = p.getBasePositionAndOrientation(bikeid)
print(cubePos,cubeOrn)
p.disconnect()
