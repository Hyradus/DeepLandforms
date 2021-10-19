#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: giacomo.nodjoumi@hyranet.info - g.nodjoumi@jacobs-university.de
"""
from detectron2.modeling import build_model
from detectron2.checkpoint import DetectionCheckpointer
from detectron2.data import MetadataCatalog
import detectron2.data.transforms as T
from detectron2.engine import DefaultTrainer
from detectron2.data import build_detection_test_loader, build_detection_train_loader
from detectron2.data import DatasetMapper
from detectron2.evaluation import COCOEvaluator
import torch
import os

class CustomPredictor:

    def __init__(self, cfg):
        self.cfg = cfg.clone()  # cfg can be modified by model
        self.model = build_model(self.cfg)
        self.model.eval()#.half()
        if len(cfg.DATASETS.TEST):
            self.metadata = MetadataCatalog.get(cfg.DATASETS.TEST[0])

        checkpointer = DetectionCheckpointer(self.model)
        checkpointer.load(cfg.MODEL.WEIGHTS)

        self.aug = T.ResizeShortestEdge(
            [cfg.INPUT.MIN_SIZE_TEST, cfg.INPUT.MIN_SIZE_TEST], cfg.INPUT.MAX_SIZE_TEST
        )

        self.input_format = cfg.INPUT.FORMAT
        assert self.input_format in ["RGB", "BGR"], self.input_format

    def __call__(self, original_images):
    
        with torch.no_grad():  # https://github.com/sphinx-doc/sphinx/issues/4258
            # Apply pre-processing to image.
            inputs =[]
            for om in original_images:
                if self.input_format == "RGB":
                    # whether the model expects BGR inputs or RGB
                    om = om[:, :, ::-1]
                height, width = om.shape[:2]
                image = self.aug.get_transform(om).apply_image(om)
                image = torch.as_tensor(image.astype("float32").transpose(2, 0, 1))
                inputs.append({"image": image, "height": height, "width": width})

            #with torch.cuda.amp.autocast():
            predictions = self.model(inputs)
            return predictions
            
            
class Trainer(DefaultTrainer):
    @classmethod

    def build_evaluator(cls, cfg, dataset_name, output_folder=None):
        if output_folder is None:
            output_folder = os.path.join(cfg.OUTPUT_DIR, "inference")
        return COCOEvaluator(dataset_name, cfg, True, output_folder)
  
    @classmethod
    def build_train_loader(cls, cfg):
        
        augs = [
                T.RandomBrightness(0.9, 1.1),
                T.RandomContrast(0.9,1.1),
                T.RandomFlip(prob=0.5)
        ]
        cmapper = DatasetMapper(cfg, is_train=True, augmentations=augs)
        return build_detection_train_loader(cfg, mapper=cmapper)
    
    @classmethod
    def build_test_loader(cls, cfg, dataset_name):
        
        augs = [
                T.RandomBrightness(0.9, 1.1),
                T.RandomContrast(0.9,1.1),
                T.RandomFlip(prob=0.5)
        ]
        cmapper = DatasetMapper(cfg, is_train=True, augmentations=augs)
        return build_detection_test_loader(cfg,dataset_name, mapper=cmapper)
            