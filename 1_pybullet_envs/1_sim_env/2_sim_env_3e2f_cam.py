from collections import namedtuple

import pybullet as p
import time
import pybullet_data
import numpy as np


physicsClient = p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setPhysicsEngineParameter(enableFileCaching=0)
p.setGravity(0,0,-10)
planeId = p.loadURDF("plane.urdf", [0, 0, -0.001])

startPos = [0,0,0]
startOrientation = p.getQuaternionFromEuler([0,0,0])
#bikeid = p.loadURDF("./bicycle/bike.urdf", startPos, startOrientation)
robotid = p.loadURDF("../ur3e/ur3e.urdf", [0, 0, 0])
numJoints = p.getNumJoints(robotid)
print('   *** robot ur3e numjoints: ', numJoints)
joint_ids = [p.getJointInfo(robotid, i) for i in range(p.getNumJoints(robotid))]
joint_ids = [j[0] for j in joint_ids if j[2] == p.JOINT_REVOLUTE]


for i in range(p.getNumJoints(robotid)):
    print("   *** ", p.getJointInfo(robotid, i)[0:2])
    # self.joint_ids = [p.getJointInfo(self.robot_id, i)


print()
home_joints = np.array([-0.5, -0.5, 0.5, -0.5, -0.5, 0]) * np.pi
# home_joints = (np.pi/2, -np.pi/2, np.pi/2, -np.pi/2, 3 * np.pi/2, 0)
for i in range(len(joint_ids)):
    print("   *** set joint state", p.getJointInfo(robotid, joint_ids[i])[0:2])
    p.resetJointState(robotid, joint_ids[i], home_joints[i])

pos = [0.1339999999999999, -1, 0.5]
#pos = [0.1339999999999999, -0.49199999999872496, 0.5]
rot = p.getQuaternionFromEuler([np.pi, 0, np.pi])
urdf = "../onrobot_2fg7_description_1/urdf/onrobot_2fg7_upload_2.urdf"
robotiq_gripper_simple = p.loadURDF(urdf, pos, rot)
print('gripper urdf:', urdf)


print()
print('   !!! gripper info')
grippernumJoints = p.getNumJoints(robotiq_gripper_simple)
print('   *** gripper 2fg7 numjoints: ', grippernumJoints)
for i in range(p.getNumJoints(robotiq_gripper_simple)):
    print("   *** ", p.getJointInfo(robotiq_gripper_simple, i)[0:2])
    # self.joint_ids = [p.getJointInfo(self.robot_id, i)


# connect the robot with the gripper
p.createConstraint(robotid, 9, robotiq_gripper_simple, 0,
                                  jointType=p.JOINT_FIXED, jointAxis=[0, 0, 0],
                                  parentFramePosition=[0, 0, 0], childFramePosition=[0, 0, -0.07],
                                  childFrameOrientation=p.getQuaternionFromEuler([0, 0, np.pi / 2]))


# integrate the camera
basePos, baseOrn = p.getBasePositionAndOrientation(robotid) # Get model position
p.resetDebugVisualizerCamera( cameraDistance=0.5, cameraYaw=75, cameraPitch=-20, cameraTargetPosition=basePos) # fix camera onto model

# try with the camera
#vmat = p.computeViewMatrixFromYawPitchRoll(cameraTargetPosition=[0.5,0,0], distance=2, yaw=0, pitch=0, roll=0, upAxisIndex=2)
#pmat = p.computeProjectionMatrixFOV(fov=60, aspect=(128 / 128), nearVal=0.01, farVal=5)
#cam1 = (vmat, pmat)
#vmat = p.computeViewMatrixFromYawPitchRoll(cameraTargetPosition=[0.5,0,0], distance=2, yaw=90, pitch=0, roll=0, upAxisIndex=2)
#pmat = p.computeProjectionMatrixFOV(fov=60, aspect=(128 / 128), nearVal=0.01, farVal=5)
#cam2 = (vmat, pmat)
#vmat = p.computeViewMatrixFromYawPitchRoll(cameraTargetPosition=[0.5,0,0], distance=2, yaw=90, pitch=-90, roll=0, upAxisIndex=2)
#pmat = p.computeProjectionMatrixFOV(fov=60, aspect=(128 / 128), nearVal=0.01, farVal=5)
#cam3 = (vmat, pmat)




# load the objects
config = {'pick':  ['yellow block', 'green block', 'blue block'],
          'place': []}


COLORS = {
    "blue":   (78/255,  121/255, 167/255, 255/255),
    "red":    (255/255,  87/255,  89/255, 255/255),
    "green":  (89/255,  169/255,  79/255, 255/255),
    "yellow": (237/255, 201/255,  72/255, 255/255),
}

PIXEL_SIZE = 0.00267857
BOUNDS = np.float32([[-0.3, 0.3], [-0.8, -0.2], [0, 0.15]])  # X Y Z


obj_name_to_id = {}
obj_names = list(config["pick"]) + list(config["place"])
obj_xyz = np.zeros((0, 3))
for obj_name in obj_names:
    if ("block" in obj_name) or ("bowl" in obj_name):
        # Get random position 15cm+ from other objects.
        while True:
            rand_x = np.random.uniform(BOUNDS[0, 0] + 0.1, BOUNDS[0, 1] - 0.1)
            rand_y = np.random.uniform(BOUNDS[1, 0] + 0.1, BOUNDS[1, 1] - 0.1)
            rand_xyz = np.float32([rand_x, rand_y, 0.03]).reshape(1, 3)
            if len(obj_xyz) == 0:
                obj_xyz = np.concatenate((obj_xyz, rand_xyz), axis=0)
                break
            else:
                nn_dist = np.min(np.linalg.norm(obj_xyz - rand_xyz, axis=1)).squeeze()
                if nn_dist > 0.15:
                    obj_xyz = np.concatenate((obj_xyz, rand_xyz), axis=0)
                    break

        object_color = COLORS[obj_name.split(" ")[0]]
        object_type = obj_name.split(" ")[1]
        object_position = rand_xyz.squeeze()
        if object_type == "block":
            object_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.02, 0.02, 0.02])
            object_visual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.02, 0.02, 0.02])
            object_id = p.createMultiBody(0.01, object_shape, object_visual,
                                                 basePosition=object_position)

        p.changeVisualShape(object_id, -1, rgbaColor=object_color)
        obj_name_to_id[obj_name] = object_id

# Re-enable rendering.
# p.configureDebugVisualizer(p.COV_ENABLE_RENDERING, 1)



for i in range (10000):
    p.stepSimulation()
    time.sleep(1./240.)
cubePos, cubeOrn = p.getBasePositionAndOrientation(robotid)
print(cubePos,cubeOrn)
p.disconnect()
