import pybullet
import numpy as np
import os
import pybullet_data
from agent_gripper_2FG7 import Gripper_2FG7
import time
from agent_eyes_camera import EyesCamera

BOUNDS = np.float32([[-0.3, 0.3], [-0.8, -0.2], [0, 0.15]])  # X Y Z

config = {'pick':  ['yellow block', 'green block', 'blue block',
                    'yellow brick_small', 'green cylinder', 'green roof', 'red triangle'],
          'place': []}

COLORS = {
    "blue":   (78/255,  121/255, 167/255, 255/255),
    "red":    (255/255,  87/255,  89/255, 255/255),
    "green":  (89/255,  169/255,  79/255, 255/255),
    "yellow": (237/255, 201/255,  72/255, 255/255),

}

PIXEL_SIZE = 0.00267857



class SimulationEnv():

    def __init__(self):
        physicsClient = pybullet.connect(pybullet.GUI)
        pybullet.setAdditionalSearchPath(pybullet_data.getDataPath())
        #pybullet.configureDebugVisualizer(pybullet.COV_ENABLE_GUI, 0)
        pybullet.setPhysicsEngineParameter(enableFileCaching=0)
        pybullet.setGravity(0, 0, -10)

        #self.home_joints = (np.pi / 2, -np.pi / 2, np.pi / 2, -np.pi / 2, 3 * np.pi / 2, 0.5)  # Joint angles: (J0, J1, J2, J3, J4, J5).
        self.home_joints = np.array([-0.5, -0.5, 0.5, -0.5, -0.5, 0.5]) * np.pi
        self.home_ee_euler = (np.pi, 0, np.pi)  # (RX, RY, RZ) rotation in Euler angles.
        self.ee_link_id = 9  # Link ID of UR5 end effector.
        self.tip_link_id = 10  # Link ID of gripper finger tips.
        self.gripper = None

    def reset(self):
        pybullet.resetSimulation(pybullet.RESET_USE_DEFORMABLE_WORLD)
        pybullet.setGravity(0, 0, -9.8)
        self.cache_video = []

        # Temporarily disable rendering to load URDFs faster.
        #pybullet.configureDebugVisualizer(pybullet.COV_ENABLE_RENDERING, 0)

        # Add robot.
        startPos = [0, 0, 0]
        startOrientation = pybullet.getQuaternionFromEuler([0, 0, 0])
        #planeId = pybullet.loadURDF("plane.urdf", startPos, startOrientation)
        planeId = pybullet.loadURDF("plane.urdf", [0, 0, -0.001])
        #self.robot_id = pybullet.loadURDF("../ur3e/ur3e.urdf", [0, 0, 0], flags=pybullet.URDF_USE_MATERIAL_COLORS_FROM_MTL)

        self.robot_id = pybullet.loadURDF("ur3e/ur3e.urdf", [0, 0, 0])
        self.ghost_id = pybullet.loadURDF("ur3e/ur3e.urdf", [0, 0, -10])  # For forward kinematics.
        self.joint_ids = [pybullet.getJointInfo(self.robot_id, i) for i in range(pybullet.getNumJoints(self.robot_id))]
        self.joint_ids = [j[0] for j in self.joint_ids if j[2] == pybullet.JOINT_REVOLUTE]

        # Move robot to home configuration.
        for i in range(len(self.joint_ids)):
            pybullet.resetJointState(self.robot_id, self.joint_ids[i], self.home_joints[i])

        # Add gripper.
        print()
        print('   *** adding the gripper')
        #if self.gripper is not None:
        #    while self.gripper.constraints_thread.is_alive():
        #        self.constraints_thread_active = False
        self.gripper = Gripper_2FG7(self.robot_id, self.ee_link_id)
        #self.gripper.release()
        print('   *** adding the gripper done')


        # Add workspace.
        print()
        print('   *** constructing the workspace')
        #plane_shape = pybullet.createCollisionShape(pybullet.GEOM_BOX, halfExtents=[0.3, 0.3, 0.001])
        #plane_visual = pybullet.createVisualShape(pybullet.GEOM_BOX, halfExtents=[0.3, 0.3, 0.001])
        #plane_id = pybullet.createMultiBody(0, plane_shape, plane_visual, basePosition=[0, -0.5, 0])
        #pybullet.changeVisualShape(plane_id, -1, rgbaColor=[0.2, 0.2, 0.2, 1.0])
        self.load_objects()
        print('   *** constructing the workspace done')



        print()
        print('   *** set onrobot_camera function')
        #self.camera = EyesCamera(self.robot_id, self.ee_link_id)
        self.set_camera()
        print('   *** set onrobot_camera function done')


        # Re-enable rendering.
        #pybullet.configureDebugVisualizer(pybullet.COV_ENABLE_RENDERING, 1)

        #for _ in range(20000):
       #     pybullet.stepSimulation()
        #    self.set_camera()



        #return self.get_observation()

    def load_objects(self):
        # Load objects according to config.
        self.config = config
        self.obj_name_to_id = {}
        obj_names = list(self.config["pick"]) + list(self.config["place"])
        print('   *** Object names: ', obj_names)
        obj_xyz = np.zeros((0, 3))
        for obj_name in obj_names:
            print('object name: ', obj_name)
            rand_x = np.random.uniform(BOUNDS[0, 0] + 0.1, BOUNDS[0, 1] - 0.1)
            rand_y = np.random.uniform(BOUNDS[1, 0] + 0.1, BOUNDS[1, 1] - 0.1)
            rand_xyz = np.float32([rand_x, rand_y, 0.03]).reshape(1, 3)
            object_position = rand_xyz.squeeze()

            object_color = COLORS[obj_name.split(" ")[0]]
            object_type = obj_name.split(" ")[1]


            if ("block" in obj_name) or ("bowl" in obj_name):

                # Get random position 15cm+ from other objects.




                if object_type == "block":
                    object_shape = pybullet.createCollisionShape(pybullet.GEOM_BOX, halfExtents=[0.02, 0.02, 0.02])
                    object_visual = pybullet.createVisualShape(pybullet.GEOM_BOX, halfExtents=[0.02, 0.02, 0.02])
                    object_id = pybullet.createMultiBody(0.01, object_shape, object_visual,
                                                         basePosition=object_position)
                elif object_type == "bowl":
                    object_position[2] = 0
                    object_id = pybullet.loadURDF("bowl/bowl.urdf", object_position, useFixedBase=1)
            else:
                print()
                object_id = pybullet.loadURDF("../object/"+object_type+".urdf", object_position, useFixedBase=1)

            pybullet.changeVisualShape(object_id, -1, rgbaColor=object_color)
            self.obj_name_to_id[obj_name] = object_id



    def get_current_pose(self):
        linkstate = pybullet.getLinkState(self.robot_id, self.ee_link_id, computeForwardKinematics=True)
        position, orientation = linkstate[0], linkstate[1]
        return (position, orientation)

    def set_camera(self):
        fov, aspect, nearplane, farplane = 60, 1.0, 0.01, 100
        projection_matrix = pybullet.computeProjectionMatrixFOV(fov, aspect, nearplane, farplane)
        interval = 0.2
        # Center of mass position and orientation (of link-7)
        com_p, com_o, _, _, _, _ = pybullet.getLinkState(self.robot_id, self.ee_link_id, computeForwardKinematics=True)

        print()
        print('   *** add object')
        print('   *** position  :', com_p)
        print('   *** oritation :', com_o)
        print('   *** the np.pi value: ', np.pi, 0.5 * np.pi)
        com_p_o = (com_p[0] + interval, com_p[1] - interval, com_p[2] + interval)
        object_shape = pybullet.createCollisionShape(pybullet.GEOM_BOX, halfExtents=[0.01, 0.02, 0.01])
        object_visual = pybullet.createVisualShape(pybullet.GEOM_BOX, halfExtents=[0.01, 0.02, 0.01])
        #object_id = pybullet.createMultiBody(0.01, object_shape, object_visual, basePosition=com_p_o)
        print('   *** add object done')

        print()
        print('   *** get link position before: ', com_p)
        # com_p = (com_p[0]+interval, com_p[1]-interval, com_p[2]+interval)
        print('   *** get link position after : ', com_p)

        print()
        print('   *** add onrobot_camera urdf')
        # com_p = (com_p[0]+interval, com_p[1]-interval, com_p[2]+interval)
        #self.camera = pybullet.loadURDF("../onrobot_camera/onrobot_eyes.urdf", [0, -1, 0])
        print('   *** add onrobot_camera urdf done')




        rot_matrix = pybullet.getMatrixFromQuaternion(com_o)
        print(com_o)
        print(rot_matrix)
        rot_matrix = np.array(rot_matrix).reshape(3, 3)

        # Initial vectors
        init_camera_vector = (0, 0, 1)  # z-axis
        init_up_vector = (0, 1, 0)  # y-axis
        init_partial_vecor = (1, 0, 0)  # x-axis

        # Rotated vectors
        camera_vector = rot_matrix.dot(init_camera_vector)
        up_vector = rot_matrix.dot(init_up_vector)
        partial_vector = rot_matrix.dot(init_partial_vecor)
        view_matrix = pybullet.computeViewMatrix(com_p, com_p + 0.1 * camera_vector, camera_vector)

        img = pybullet.getCameraImage(1000, 1000, view_matrix, projection_matrix)
        return img

    def get_observation(self):
        observation = {}

        # Render current image.
        color, depth, position, orientation, intrinsics = self.render_image()

        # Get heightmaps and colormaps.
        points = self.get_pointcloud(depth, intrinsics)
        position = np.float32(position).reshape(3, 1)
        rotation = pybullet.getMatrixFromQuaternion(orientation)
        rotation = np.float32(rotation).reshape(3, 3)
        transform = np.eye(4)
        transform[:3, :] = np.hstack((rotation, position))
        points = self.transform_pointcloud(points, transform)
        heightmap, colormap, xyzmap = self.get_heightmap(points, color, BOUNDS, PIXEL_SIZE)

        observation["image"] = colormap
        observation["xyzmap"] = xyzmap
        observation["pick"] = list(self.config["pick"])
        observation["place"] = list(self.config["place"])
        return observation

    def render_image(self, image_size=(720, 720), intrinsics=(360., 0, 360., 0, 360., 360., 0, 0, 1)):

        # Camera parameters.
        position = (0, -0.85, 0.4)
        orientation = (np.pi / 4 + np.pi / 48, np.pi, np.pi)
        orientation = pybullet.getQuaternionFromEuler(orientation)
        zrange = (0.01, 10.)
        noise = True

        # OpenGL onrobot_camera settings.
        lookdir = np.float32([0, 0, 1]).reshape(3, 1)
        updir = np.float32([0, -1, 0]).reshape(3, 1)
        rotation = pybullet.getMatrixFromQuaternion(orientation)
        rotm = np.float32(rotation).reshape(3, 3)
        lookdir = (rotm @ lookdir).reshape(-1)
        updir = (rotm @ updir).reshape(-1)
        lookat = position + lookdir
        focal_len = intrinsics[0]
        znear, zfar = (0.01, 10.)
        viewm = pybullet.computeViewMatrix(position, lookat, updir)
        fovh = (image_size[0] / 2) / focal_len
        fovh = 180 * np.arctan(fovh) * 2 / np.pi

        # Notes: 1) FOV is vertical FOV 2) aspect must be float
        aspect_ratio = image_size[1] / image_size[0]
        projm = pybullet.computeProjectionMatrixFOV(fovh, aspect_ratio, znear, zfar)

        # Render with OpenGL onrobot_camera settings.
        _, _, color, depth, segm = pybullet.getCameraImage(
            width=image_size[1],
            height=image_size[0],
            viewMatrix=viewm,
            projectionMatrix=projm,
            shadow=1,
            flags=pybullet.ER_SEGMENTATION_MASK_OBJECT_AND_LINKINDEX,
            renderer=pybullet.ER_BULLET_HARDWARE_OPENGL)

        # Get color image.
        color_image_size = (image_size[0], image_size[1], 4)
        color = np.array(color, dtype=np.uint8).reshape(color_image_size)
        color = color[:, :, :3]  # remove alpha channel
        if noise:
            color = np.int32(color)
            color += np.int32(np.random.normal(0, 3, color.shape))
            color = np.uint8(np.clip(color, 0, 255))

        # Get depth image.
        depth_image_size = (image_size[0], image_size[1])
        zbuffer = np.float32(depth).reshape(depth_image_size)
        depth = (zfar + znear - (2 * zbuffer - 1) * (zfar - znear))
        depth = (2 * znear * zfar) / depth
        if noise:
            depth += np.random.normal(0, 0.003, depth.shape)

        intrinsics = np.float32(intrinsics).reshape(3, 3)
        return color, depth, position, orientation, intrinsics





env = SimulationEnv()
env.reset()

for i in range (10000):
    pybullet.stepSimulation()
    time.sleep(1./240.)

cubePos, cubeOrn = pybullet.getBasePositionAndOrientation(env.robot_id)
print(cubePos,cubeOrn)
pybullet.disconnect()
