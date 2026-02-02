"""Config for locating task annotation JSONs & images.

IMPORTANT:
- This file is a *direct copy of the important parts* of your annotation platform script's TASK_CONFIG.
- Please verify paths on your machine.
"""

import os

# Global base path (from your platform)
BASE_DIR = "/PATH/TO/YOUR/BASE_DIR"

TASK_CONFIG = {
    "2-Tasks": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-I/Multi-Tasks/2-Tasks.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-I/Multi-Tasks/"),
        "image_root": BASE_DIR
    },
    "3-Tasks": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-I/Multi-Tasks/3-Tasks.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-I/Multi-Tasks/"),
        "image_root": BASE_DIR
    },
    "Addition": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-I/Addition/Addition.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-I/Addition/"),
        "image_root": BASE_DIR,
    },
    "Removal": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-I/Removal/Removal.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-I/Removal/"),
        "image_root": BASE_DIR,
    },
    "Replacement": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-I/Replacement/Replacement.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-I/Replacement/"),
        "image_root": BASE_DIR,
    },
    "Translation": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-I/Translation/Translation.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-I/Translation/"),
        "image_root": BASE_DIR,
    },
    "Flow": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-III/Flow/flow.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-III/Flow/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Dimension-III/Flow/"),
    },
    "Light_Control": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-III/Light_Control/light_control.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-III/Light_Control/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Dimension-III/Light_Control/"),
    },
    "Billiards": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-III/Billiards/Billiards.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-III/Billiards/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Dimension-III/Billiards/"),
    },
    "Draft_Instantiation": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-II/Draft_Instantiation/draft_instantiation.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-II/Draft_Instantiation/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Dimension-II/Draft_Instantiation/"),
    },
    "Reorientation": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-II/Reorientation/Reorientation.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-II/Reorientation/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Dimension-II/Reorientation/"),
    },
    "Pose_Control": {
        "json_path": os.path.join(BASE_DIR, "Tasks/Dimension-II/Pose_Control/dataset.json"),
        "task_dir": os.path.join(BASE_DIR, "Tasks/Dimension-II/Pose_Control/"),
        "image_root": os.path.join(BASE_DIR, "Tasks/Dimension-II/Pose_Control/"),
    },
}

# Where your platform saves visual-instruction layers by default
SAVE_ROOT_DIR = "annotated_images"
