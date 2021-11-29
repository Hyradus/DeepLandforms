# **DeepLandforms**

Author: giacomo.nodjoumi@hyranet.info - g.nodjoumi@jacobs-university.de
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5734621.svg)](https://doi.org/10.5281/zenodo.5734621)

## DeepLandforms Training

With this notebook, users can train instance segmentation models on custom dataset of georeferenced images.
The models are based on state-of-the-art general purpose architectures, available [here](https://github.com/facebookresearch/detectron2).
Despite several types of networks are supported, such as object detection, image segmentation ad instance segmentation, and available in the above repository, this notebook and the complementary **DeepLandrorms-Segmentation** notebook are specific for instance segmentation architectures for georefernced images.

### Usage

* Prepare the dataset in COCO label format, using provided **LabelMe** container or else.
* Put or link the dataset into the **DeepLandforms** *.env* file
* Run docker-compose up
* Edit the *configs* section by editing the following parameters:
------------------------------------------------------------------
| **Parameter** | **Function** | **Common Values** |
| ---- | ---- | ---- |
| **cfg.merge_from_file(model_zoo.get_config_file(""))** | Model Architecture | MASK-R-CNN in this work |
| **cfg.TEST.EVAL_PERIOD** |  N° of epochs after an evaluation is performed | depending on SOLVER.MAX_ITER, usually every 1/10 of ITER, e.g. every 1000 on a 10000 iter |
| **cfg.DATALOADER.NUM_WORKERS** | Number of workers for dataloader | usually correspond to cpu cores |
| **cfg.MODEL.WEIGHTS** | model_zoo.get_checkpoint_url("") | Optional but advised to start from a pretrained model from the model zoo, MUST be of the same architecture of the get_config_file. see default values as example. |
| **cfg.SOLVER.IMS_PER_BATCH** | How many image to be ingested, depends on the performance of the GPU, especiall VRAM |  up to 8 for 8GB VRAM |
| **cfg.SOLVER.BASE_LR** | learning rate | 0.0002 is a good starting point |
| **cfg.SOLVER.MAX_ITER** | N° of epochs | Rise up for low mAP, lower to prevent overfitting |
| **cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE** | parameter to sample a subset of proposals coming out of RPN to calculate cls and reg loss during training. | multiple of 2, commonly 64 |
------------------------------------------------------------------
Then just execute the notebook and monitor the training in **Tensorboard** container.


## DeepLandforms Segmentation

With this notebook, users can use custom trained models for instance segmentation models on custom dataset of georeferenced images.
The output consist of a folder containing:
* Source Images in which at least one detection occurred
* Label file in COCO json format for each image
* Geopackage containing a single layer with image name, confidence leve, class.

### Usage

* Put or link the dataset into the **DeepLandforms** *.env* file
* Run docker-compose up
* Edit the *configs* section by editing the following parameters:
------------------------------------------------------------------
| **Parameter** | **Function** | **Common Values** |
| ---- | ---- | ---- |
| **batch_size** | N° of images to be processed at once | Depending on VRAM and image size, up to 8 per 8GB VRAM |
| **geopackage_name** |  Name of the final geopackage |  |
| **proj_geopackage_name** | Name of the final geopackage in custom projection | |
| **model_path** | local path and name of the model  | it should start with /pre-trained_models/ |
| **model_yaml** | Model Architecture | MASK-R-CNN in this work | EDIT according to trained model selected |
| **dst_crs** | CRS of the geopackage | provide as WKT or proj4 |

------------------------------------------------------------------
Then just execute the notebook and monitor the training in **Tensorboard** container.

## Funding
*This study is within the Europlanet 2024 RI and EXPLORE project, and it has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 871149 and No 101004214.*
