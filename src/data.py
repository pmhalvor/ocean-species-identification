from fathomnet.models.yolov5 import YOLOv5Model
from PIL import Image
from pathlib import Path
from pycocotools.coco import COCO
from typing import List

import os 
import numpy as np 


def full_path(filename: str, prefix: str) -> str:
    return os.path.join(prefix, filename)


def category2image_ids(category: str, data: COCO) -> int:
    return data.getImgIds(catIds=data.getCatIds(catNms=[category]))


def images_per_category(
        category: str, 
        data: COCO, 
        path_prefix: 
        str="", N: 
        int=-1
    ) -> List[str]:
    return [
        full_path(r["file_name"], path_prefix) 
        for r in data.loadImgs(category2image_ids(category, data))
    ]


def detections_per_category(
        category: str,
        data: COCO, 
        model: YOLOv5Model, 
        path_prefix: str = "",
        N: int = -1,
        **kwargs
    ):
    image_paths = images_per_category(category, data, path_prefix)

    # run inference on N images
    return  model.forward(image_paths[:N])


def anns_per_category(category: str, data: COCO, N: int=-1):
    image_ids = category2image_ids(category, data)
    return [
        # for-loop needed for preprocessing annotation
        preprocess_anns(
            data.loadAnns(data.getAnnIds(imgIds=id))
        )
        for id in image_ids[:N]
    ]


def preprocess_anns(anns: List[dict]):
    """
    Preprocess annotation to match detection format
    Each image is annotated with a list of annotations. 
    Each element in this list is a dict, where we are interested in the following keys:
    - bbox: [x, y, width, height]
    - category_id: int

    Let's convert the input to the following format:
    [
        (x1, y1, x2, y2, category_id),
        ...
    ]

    Args:
        anns (list[dict]): annotation

    Returns:
        list[tuple]: preprocessed annotation
    """
    return [
        (
            a["bbox"][0],
            a["bbox"][1],
            a["bbox"][0] + a["bbox"][2],  # x2 = x1 + width
            a["bbox"][1] + a["bbox"][3],  # y2 = y1 + height
            a["category_id"],
        )
        for a in anns
    ]