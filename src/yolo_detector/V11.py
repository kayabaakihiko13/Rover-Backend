from typing import Any,List,Tuple
import numpy as np
import onnxruntime as ort
import yaml
import cv2

class Yolov11Detector:
    def __init__(self,model_path:str,label_yaml:str,
                 conf_thresh:float=0.25, iou_thresh:float=0.7,optimize:bool=True):
        """Class ini merupakan Arsitketur 
        Yolov11 detector native"""
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        # menyimpan predict nya
        self.clasess = None
        # load kelas from yaml file
        with open(label_yaml,"r") as f:
            self.classes = yaml.safe_load(f)["names"]
        opts = ort.SessionOptions()
        if optimize:
            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 1 # dibawah ini 
            opts.add_session_config_entry("session.intra_op.allow_spinning", "0")
            self.session = ort.InferenceSession(model_path,opts,providers=['CPUExecutionProvider'])
        else:
            self.session = ort.InferenceSession(model_path)
        
        input_shape  = self.session.get_inputs()[0].shape
        self.INPUT_H = input_shape[2]
        self.INPUT_W = input_shape[3]


    def preprocess(self,img_arr:np.ndarray)-> np.ndarray:
        blob = cv2.dnn.blobFromImage(
            img_arr,scalefactor=1/255.0,
            size=(self.INPUT_W,self.INPUT_H),
            mean=(0,0,0),swapRB=True,crop=False
        )
        return blob

    def nms(self,boxes, scores:float, iou_threshold: float):
        """Pure NumPy NMS"""
        boxes = np.array(boxes)
        scores = np.array(scores)

        x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(ovr <= iou_threshold)[0]
            order = order[inds + 1]

        return keep

    def postprocess(self, outputs: Any, orig_h: int, orig_w: int) -> Tuple[List[List[int]], List[float], List[int]]:
        preds = outputs[0].transpose(0, 2, 1)[0]  # [N, 4+num_classes]
        boxes_xywh, scores_all = preds[:, :4], preds[:, 4:]

        # confidence & class
        confidences = scores_all.max(axis=1)
        class_ids = scores_all.argmax(axis=1)

        # filter confidence
        mask = confidences > self.conf_thresh
        if not np.any(mask):
            return [], [], []

        boxes_xywh, confidences, class_ids = boxes_xywh[mask], confidences[mask], class_ids[mask]

        # vectorized xywh → xyxy
        scale_w, scale_h = orig_w / self.INPUT_W, orig_h / self.INPUT_H
        x, y, w, h = boxes_xywh[:, 0], boxes_xywh[:, 1], boxes_xywh[:, 2], boxes_xywh[:, 3]
        xmin = np.clip((x - w / 2) * scale_w, 0, orig_w)
        ymin = np.clip((y - h / 2) * scale_h, 0, orig_h)
        xmax = np.clip((x + w / 2) * scale_w, 0, orig_w)
        ymax = np.clip((y + h / 2) * scale_h, 0, orig_h)
        boxes = np.stack([xmin, ymin, xmax, ymax], axis=1).astype(int).tolist()

        # optional: ambil top-k kandidat sebelum NMS
        top_k = 300
        if len(confidences) > top_k:
            idx = np.argsort(-confidences)[:top_k]
            boxes = [boxes[i] for i in idx]
            confidences = confidences[idx]
            class_ids = class_ids[idx]

        # NMS
        idxs = self.nms(boxes, confidences, self.iou_thresh)
        final_boxes = [boxes[i] for i in idxs]
        final_scores = confidences[idxs].tolist()
        final_class_ids = class_ids[idxs].tolist()
        
        return final_boxes, final_scores, final_class_ids


    def detect(self, image:np.ndarray)->List:
        blob = self.preprocess(image)
        outputs = self.session.run(None, {self.session.get_inputs()[0].name: blob})
        boxes,score,class_ids= self.postprocess(outputs, image.shape[0], image.shape[1])
        return boxes,score,class_ids

