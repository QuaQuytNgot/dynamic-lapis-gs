import itertools
import os
import json
import math
from pathlib import Path
import numpy as np
import open3d as o3d
from PIL import Image
import open3d.visualization.rendering as rendering
from argparse import ArgumentParser


def read_poses(pose_json_path):
    with open(pose_json_path, 'r') as fp:
        meta = json.load(fp)

    camera_field = meta['camera_angle_x']
    poses = [np.array(frame['transform_matrix']) for frame in meta['frames'][::1]]
    poses = np.array(poses).astype(np.float32)
    return camera_field, poses

def extract_eye_up_from_camera_matrix(camera_matrix):
    R = camera_matrix[:3, :3]
    T = camera_matrix[:3, 3]
    eye = T
    up = R[:, 1]
    z = R[:, 2]
    return eye, up, z

def save_image(out_root, render):
    img = render.render_to_image()
    os.makedirs(os.path.dirname(out_root), exist_ok=True)
    o3d.io.write_image(out_root, img, 9)  # save images with black background
    image = Image.open(out_root)  # reload images
    image = image.convert('RGBA')
    data = image.getdata()
    new_data = []
    for item in data:
        if item[:3] == (0, 0, 0):
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
    image.putdata(new_data)
    image.save(out_root, 'PNG')
    return 0

# pc_path, render_dir, pose_json_dict[pose_type]
def render_2d_image(pc_path, render_dir, pose_json_path, pt_size=1, width=600, height=600, testskip=1):  # 2.2 1400*1400
    point_cloud = o3d.io.read_point_cloud(pc_path)
    point_cloud = point_cloud.voxel_down_sample(voxel_size=1.7)

    camera_point_to = point_cloud.get_axis_aligned_bounding_box().get_center()   # [281, 510, 170]
    
    
    points = np.asarray(point_cloud.points) - camera_point_to
    if "thaidancer" in pc_path:
        points /= 960.0 
    else: 
        points /= 480.0  # r~=4
    points -= (0, 0.1, 0)
    rotation_matrix = np.array([[1, 0, 0],
                                [0, 0, -1],
                                [0, 1, 0]])
    points = np.dot(points, rotation_matrix.T)
    point_cloud.points = o3d.utility.Vector3dVector(points)  # resize

    
    material = rendering.MaterialRecord()
    material.shader = "defaultUnlit"
    material.point_size = pt_size

    # initialize `render`
    render = rendering.OffscreenRenderer(width, height)
    # set render parameter
    # render.scene.set_background(np.array([1.0, 1.0, 1.0, 1.0])) # set the background to be white
    render.scene.set_background(np.array([0.0, 0.0, 0.0, 0.0])) # set the background to be transparent
    render.scene.add_geometry("pcd", point_cloud, material)
    render.scene.view.set_post_processing(False)

    camera_angle_x, ex_matrix = read_poses(pose_json_path)
    for idx, mat in enumerate(ex_matrix[::testskip]):
        # if idx % 50 == 0:
            # print('dataset' + data_root + ': ' + split + str(idx))
        output_filename = os.path.join(render_dir, f"r_{idx}.png")


        cam_eye, cam_up, cam_z = extract_eye_up_from_camera_matrix(mat)
        cam_center = cam_eye - cam_z # cam_z is the camera distance
        field_view = camera_angle_x * 180 / math.pi
        render.setup_camera(field_view,  # or 60?
                            cam_center,
                            cam_eye,
                            cam_up)
        # print(cam_center, cam_eye, np.linalg.norm(cam_z), point_cloud.get_axis_aligned_bounding_box().get_center())

        # capture the screenshot
        save_image(output_filename, render)

    del render, material


def rescale_image(image_path, resolution_scale=1):
    image = Image.open(image_path)
    width, height = image.size

    newsize = round(width/(resolution_scale)), round(height/(resolution_scale))

    return image.resize(newsize, Image.LANCZOS)



if __name__ == "__main__":
    # Set up command line argument parser

    parser = ArgumentParser(description="Render 2D images from point clouds")
    parser.add_argument("--ptcl_root", type=str, required=True, help="Path to the root directory of point clouds")
    parser.add_argument("--output_root", type=str, required=True, help="Path to the output root directory")
    parser.add_argument("--dataset_name", type=str, default="8i", help="Name of the dataset")
    parser.add_argument("--total_frame_num", type=int, default=30, help="Number of frames to process for each model")

    args = parser.parse_args()

    ptcl_root = args.ptcl_root
    output_root = args.output_root
    dataset_name = args.dataset_name
    total_frame_num = args.total_frame_num

    model_list = ['longdress', 'soldier']

    pose_json_dict = {"train": "transforms_train.json",
                    "test":  "transforms_test.json",
                    }
    
    
    resolution_scales = [1, 2, 4, 8]

    pt_size, width, height = 2, 1024, 1024

    total_frame_count = total_frame_num

    for res, model in itertools.product(resolution_scales, model_list):
        for pose_type in ["train", "test"]:

            ptcl_dir = os.path.join(ptcl_root, model, 'Ply')
            frame_count = 0
            
            # iterate the ptcl_dir for each file with .ply extension
            for file_name in sorted(os.listdir(ptcl_dir)):
                # only process the .ply files and not start with .
                if file_name.endswith(".ply") and not file_name.startswith("."):
                    frame_count += 1
                    pc_path = os.path.join(ptcl_dir, file_name)
                    frame_no = file_name.split('_')[-1].split('.')[0][-4:] # split by _ and capture the digits of the last part

                    if frame_count <= total_frame_count:
                        render_dir = os.path.join(output_root, dataset_name, model, f"{model}_res{res}", frame_no, pose_type)
                        os.makedirs(render_dir, exist_ok=True) # make the directory if not exist
                        print(f"Rendering {file_name} with resolution {res}, pose type: {pose_type}")
                        
                        if res == 1: # no need to downscale the images
                            render_2d_image(pc_path, render_dir, pose_json_dict[pose_type], pt_size=pt_size, width=width, height=height)
                        else: # downscale the images by a factor of res
                            original_render_dir = os.path.join(output_root, dataset_name, model, f"{model}_res1", frame_no, pose_type)
                            # rescale the images
                            for image_name in os.listdir(original_render_dir):
                                if image_name.endswith(".png") and not image_name.startswith("."):
                                    image_path = os.path.join(original_render_dir, image_name)
                                    new_image = rescale_image(image_path, res)
                                    new_image.save(os.path.join(render_dir, image_name))


                        # move the pose_json_dict[pose_type] to the parent dir of render_dir
                        os.system(f"cp {pose_json_dict[pose_type]} {str(Path(render_dir).parent)}")
