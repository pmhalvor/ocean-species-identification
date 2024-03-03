from src.data import detections_per_category, anns_per_category
from time import time
from pycocotools.coco import COCO
from fathomnet.models.yolov5 import YOLOv5Model

from typing import List, Any 

def calculate_iou(box1, box2):
    # Calculate intersection coordinates
    x1_intersection = max(box1[0], box2[0])
    y1_intersection = max(box1[1], box2[1])
    x2_intersection = min(box1[2], box2[2])
    y2_intersection = min(box1[3], box2[3])

    # Calculate intersection area
    intersection_area = max(0, x2_intersection - x1_intersection) * max(0, y2_intersection - y1_intersection)

    # Calculate area of each box
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    # Calculate union area
    union_area = box1_area + box2_area - intersection_area

    # Calculate IoU
    iou = intersection_area / union_area if union_area > 0 else 0

    return iou


def evaluate_bboxes(
        pred_boxes, 
        true_boxes, 
        iou_threshold=0.5, 
        id_map=None,
        one_idx=None,
        many_idx=[],
        exclude_ids=[],
        x_scale=1.0,
        y_scale=1.0,
        **kwargs
    ):
    """
    Single row evaluation of predicted and true boxes. Returns precision and recall.

    args:
        pred_boxes (list): (x1, y1, x2, y2, confidence, class_id) for each predicted box
        true_boxes (list): (x1, y1, x2, y2, class_id) for each ground truth box
        iou_threshold (float): threshold for considering a predicted box a true positive
        id_map (dict): mapping of class ids from the Benthic model to the TrashCAN model
        one_idx (int): benthic class id of the one class
        many_idx (list): trashcan class ids of the many class
        exclude_ids (list): true class ids to exclude from evaluation
    """
    tp = 0  # True positives
    fp = 0  # False positives
    fn = 0  # False negatives
    ious = []

    # Loop through predicted boxes
    for pred_box in pred_boxes:
        pred_box_coords = pred_box[:4]
        pred_class_id = int(pred_box[5])

        # important to map the Benthic model's class ids to our TrashCAN class ids
        if id_map and pred_class_id in id_map:
            pred_class_id = id_map[pred_class_id]


        # Find best matching true box
        best_iou = 0
        best_match_index = -1
        for i, true_box in enumerate(true_boxes):
            true_box_coords = true_box[:4]
            true_class_id = true_box[4]

            # scale true annotations to new image size
            true_box_coords = [
                int(coord * x_scale) if i % 2 == 0 else int(coord * y_scale)
                for i, coord in enumerate(true_box_coords)
            ]


            # ensure we handle trash labels properly! 
            if pred_class_id == one_idx and true_class_id in many_idx:
                pred_class_id = true_class_id

            # remove plants and rov from evaluation
            if true_class_id in exclude_ids:
                continue

            # Calculate IoU
            iou = calculate_iou(pred_box_coords, true_box_coords)

            # Check if IoU is greater than threshold and class IDs match
            if iou > best_iou and pred_class_id == true_class_id:
                best_iou = iou
                best_match_index = i

        # If IoU is greater than threshold, consider it a true positive
        if best_iou >= iou_threshold:
            tp += 1
            del true_boxes[best_match_index]  # Remove matched true box
        else:
            fp += 1

        ious.append(best_iou)

    # Any remaining true boxes are false negatives
    fn = len(true_boxes)

    return tp, fp, fn, ious


def calculate_precision_recall(tp, fp, fn, eps=1e-6):
    return tp / (tp + fp + eps), tp / (tp + fn + eps)


def evaluate_detections(
        detections: List[Any], 
        anns: List[dict], 
        id_map: dict=None, 
        N: int=-1, 
        return_confusion_metrics: bool=False,
        **kwargs
    ):
    """
    Evaluate detections on a single image. 
    Returns precision and recall.

    Args:
        detections (list): list of detections for a single image
        anns (list): list of annotations for a single image
    """
    tp, fp, fn, ious = 0, 0, 0, []

    for i, (pred_boxes, true_boxes) in enumerate(zip(detections.xyxy[:N], anns[:N])):
        tp_, fp_, fn_, ious_ = evaluate_bboxes(
            pred_boxes, 
            true_boxes, 
            id_map=id_map, 
            **kwargs
        )
        
        tp += tp_
        fp += fp_
        fn += fn_
        ious.extend(ious_)

    if return_confusion_metrics:
        return tp, fp, fn, ious
            
    precision, recall = calculate_precision_recall(tp, fp, fn)

    return precision, recall, ious


def print_precision_recall_iou(precision, recall, iou):
    print("Precision:", precision)
    print("Recall:", recall)
    print("Average IoU:", sum(iou) / len(iou))


def evaluate_model(
        category:str, 
        data: COCO, 
        model: YOLOv5Model, 
        id_map: dict={}, 
        verbose: bool=True,  
        N: int=-1, 
        **kwargs
    ):
    start = time()
    detections = detections_per_category(
        category=category, data=data, model=model, N=N, **kwargs
    )
    anns = anns_per_category(category=category, data=data, N=N)

    precision, recall, ious = evaluate_detections(
        detections=detections, 
        anns=anns, 
        id_map=id_map, 
        N=N, 
        **kwargs
    )

    print_precision_recall_iou(precision, recall, ious) if verbose else None
    if verbose > 1:
        detections.show()

    return {
        "precision": precision, 
        "recall": recall, 
        "iou": sum(ious) / len(ious), 
        "time": time() - start
    }
