import torch

from utilities.constants import *

# run_nms_inplace
def run_nms_inplace(preds, yolo_layer):
    """
    ----------
    Author: Damon Gwinn (gwinndr)
    ----------
    - Performs nms inplace on preds according to method and hyperparams specified by yolo_layer
    - Nms will decrease the lower of two class confidence scores of bboxes found to overlap
    - Assumes class confidence scores have already been multiplied by objectness
    - Assumes bounding box coordinate information in preds (tx,ty,tw,th) is the exact same as
      was returned from the darknet model
    ----------
    """

    if(yolo_layer.nms_kind == GREEDY_NMS):
        greedy_nms_inplace(preds)

    return

# greedy_nms_inplace
def greedy_nms_inplace(preds, nms_thresh=NMS_THRESHOLD):
    """
    ----------
    Author: Damon Gwinn (gwinndr)
    ----------
    - Performs greedy nms inplace on preds
    - Greedy nms forces the lower of two same class probabilities to 0 if the IOU between their respective
      bounding boxes is greater than NMS_THRESHOLD
    - Assumes class confidence scores have already been multiplied by objectness
    - Assumes bounding box coordinate information in preds (tx,ty,tw,th) is the exact same as
      was returned from the darknet model
    ----------
    """

    bbox_attrs = preds[..., YOLO_TX:YOLO_TH+1]
    class_probs = preds[..., YOLO_CLASS_START:]

    bboxes = torch.zeros(bbox_attrs.shape, dtype=bbox_attrs.dtype, device=bbox_attrs.device)

    half_w = bbox_attrs[..., YOLO_TW] / 2
    half_h = bbox_attrs[..., YOLO_TH] / 2

    # Bounding box top-left (x1y1) and bottom-right (x2y2) coordinates
    bboxes[..., BBOX_X1] = bbox_attrs[..., YOLO_TX] - half_w
    bboxes[..., BBOX_Y1] = bbox_attrs[..., YOLO_TY] - half_h
    bboxes[..., BBOX_X2] = bbox_attrs[..., YOLO_TX] + half_w
    bboxes[..., BBOX_Y2] = bbox_attrs[..., YOLO_TY] + half_h

    # Doing a cartesian product via for loops (TODO: Could be optimized to remove the for loop I'm sure)
    for i, bbox in enumerate(bboxes[:-1]):
        bboxes_b = bboxes[i+1:]
        bboxes_a = bbox.expand_as(bboxes_b)

        iou = bbox_iou(bboxes_a, bboxes_b)
        thresh_mask = iou > nms_thresh

        class_b = class_probs[i+1:]
        class_b_thresh = class_b[thresh_mask]
        class_a = class_probs[i].expand_as(class_b_thresh)

        class_zero_a = class_a < class_b_thresh
        class_zero_b = ~class_zero_a

        # masked_select does not share storage with the original tensor
        zero_mask_b = torch.zeros(class_b.size(), device=class_zero_b.device, dtype=class_zero_b.dtype)
        zero_mask_b[thresh_mask] = class_zero_b

        # If two bboxes overlap set the lower class probabilities to 0
        class_a[class_zero_a] = 0
        class_b[zero_mask_b] = 0

    return

# bbox_iou
# Modified from https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc
def bbox_iou(bboxes_a, bboxes_b):
    """
    ----------
    Author: Johannes Meyer (meyerjo)
    Modified: Damon Gwinn (gwinndr)
    ----------
    - Computes IOU elementwise between the bboxes in a and the bboxes in b
    - Code modified from https://gist.github.com/meyerjo/dd3533edc97c81258898f60d8978eddc
    ----------
    """

    # determine the (x, y)-coordinates of the intersection rectangle
    xA = torch.max(bboxes_a[..., BBOX_X1], bboxes_b[..., BBOX_X1])
    yA = torch.max(bboxes_a[..., BBOX_Y1], bboxes_b[..., BBOX_Y1])
    xB = torch.min(bboxes_a[..., BBOX_X2], bboxes_b[..., BBOX_X2])
    yB = torch.min(bboxes_a[..., BBOX_Y2], bboxes_b[..., BBOX_Y2])

    # compute the area of intersection rectangle
    interArea = torch.clamp(xB - xA, min=0) * torch.clamp(yB - yA, min=0)

    # compute the area of both the prediction and ground-truth
    # rectangles
    bboxes_aArea = (bboxes_a[..., BBOX_X2] - bboxes_a[..., BBOX_X1]) * (bboxes_a[..., BBOX_Y2] - bboxes_a[..., BBOX_Y1])
    bboxes_bArea = (bboxes_b[..., BBOX_X2] - bboxes_b[..., BBOX_X1]) * (bboxes_b[..., BBOX_Y2] - bboxes_b[..., BBOX_Y1])

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / (bboxes_aArea + bboxes_bArea - interArea)

    # return the intersection over union value
    return iou