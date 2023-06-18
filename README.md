# **DeepLandforms**

Author: giacomo.nodjoumi@hyranet.info - g.nodjoumi@jacobs-university.de

Thise repository contains all the code to build and run *DeepLandforms* a novel toolset that provides all the necessary tools to train an instance segmentation model for landforms detections. Tools includes, data preparation, labeling, training, monitoring and inference.

## Workflow

<img src="Readme/Figure-3-flowchart.png?raw=true" title="DeepLandforms workflow" width="1000"/>

## Components
### ImageProcessingUtils
[![DOI](https://zenodo.org/badge/287286230.svg)](https://zenodo.org/badge/latestdoi/287286230)

ImageProcessingUtils is a Jupyter Notebook for processing georeferenced images such as GeoTiff, JP2, png/jpeg+world file, CUB (USGS ISIS).
With this tool is possible to perform single to multiple tasks including:

* convert to GeoTiff, Cloud Optimize GeoTiff (COG), JP2, png/jpeg+world file, CUB (USGS ISIS)
* rescale images pixel resolution
* create tiles for images larger than user-defined size limit
* remove black borders for images/tiles
* crop images/tiles with a 1:1 centered aspect ration

The notebook is served through a docker image containing all required packages.
see [official repository](https://github.com/Hyradus/ImageProcessingUtils)

### Labelme
Dockerized version of [wkentaro/labelme](https://github.com/wkentaro/labelme)

### DeepLandforms
Main Notebooks to perform training and inference on geo-referenced data.
DeepLandforms now two separate main folders

Detectron2 has been removed from default packages.

New defaut available packages:
* [ultralytics](https://github.com/ultralytics/ultralytics)
* [SAHI](https://github.com/obss/sahi)
* [super-gradients](https://github.com/Deci-AI/super-gradients)
* [segment-geospatial](https://github.com/opengeos/segment-geospatial)

#### Ultralytics - YOLOv8
___________________________________________________________

Jocher, G., Chaurasia, A., & Qiu, J. (2023). YOLO by Ultralytics (Version 8.0.0) [Computer software]. https://github.com/ultralytics/ultralytics

**DeepLandforms-Training-YOLOv8.ipynb**

With this notebook, users can train object detection and instance segmentation models on custom dataset of georeferenced images.
The models are based on state-of-the-art general purpose architectures, available [here](https://github.com/ultralytics/ultralytics).

**DeepLandforms-Inference-YOLOv8.ipynb**

With this notebook, users can use custom [YOLOv8](https://github.com/ultralytics/ultralytics) trained models for object detection and instance segmentation models on custom dataset of georeferenced images.
Results can be visualized directly in the noteboo using leafmap and WMS backend.

The output consist of a folder containing:
* Crop of the detections (georeferenced)
* Label file in YOLO txt format for object detection
* Geopackage containing a single layer with image name, confidence leve, class.


#### Detectron2
___________________________________________________________
**DeepLandforms-Training Notebook**

With this notebook, users can train instance segmentation models on custom dataset of georeferenced images.
The models are based on state-of-the-art general purpose architectures, available [here](https://github.com/facebookresearch/detectron2).
Despite several types of networks are supported, such as object detection, image segmentation ad instance segmentation, and available in the above repository, this notebook and the complementary **DeepLandrorms-Segmentation** notebook are specific for instance segmentation architectures for georefernced images.

**DeepLandforms Segmentation Notebook**

With this notebook, users can use custom trained models for instance segmentation models on custom dataset of georeferenced images.
The output consist of a folder containing:
* Source Images in which at least one detection occurred
* Label file in COCO json format for each image
* Geopackage containing a single layer with image name, confidence leve, class.

### Tensorboard

Dockerized version of the popular framework for visualizing training metrics.
See [here](https://www.tensorflow.org/tensorboard)


## Requirements

* 15 GB of free disk space
* Ubuntu OS or other distro
* Docker
* Nvidia-docker
* Nvidia GPU
* 16GB RAM (more is better, especially when processing very high-resolution images)
* 8+ cpu cores

## Tutorial

See the tutorial folder.

Needs to be updated.

## Troubleshooting

### Labelme 


#### Labelme not starting due to missing display
The solution is to run the following command:
```
xhost +local:docker 
```
and then again build the container:
```
docker-compose up --build
```

## To-DO

* [ ] Update tutorial
* [ ] Remove nvidia-docker strict requirement
* [X] Remove Detectron2 and make it optional 
* [X] Implement additional architectures (e.g. U-Net, YOLO)
* [X] Implement Segment-Anything stage
* [ ] Deploy Segment-Anything stage

## How to Cite

### Plain-text
Nodjoumi, G., Pozzobon, R., Sauro, F., & Rossi, A. P. (2022). DeepLandforms: A Deep Learning Computer Vision toolset applied to a prime use case for mapping planetary skylights. Earth and Space Science, 10, e2022EA002278. https://doi.org/10.1029/2022EA002278

### BibTex
@article{https://doi.org/10.1029/2022EA002278,
author = {Nodjoumi, Giacomo and Pozzobon, Riccardo and Sauro, Francesco and Rossi, Angelo Pio},
title = {DeepLandforms: A Deep Learning Computer Vision toolset applied to a prime use case for mapping planetary skylights},
journal = {Earth and Space Science},
volume = {n/a},
number = {n/a},
pages = {e2022EA002278},
keywords = {Mapping, Mars, Pits, Skylight, Deep Learning, Toolset},
doi = {https://doi.org/10.1029/2022EA002278},
url = {https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2022EA002278},
eprint = {https://agupubs.onlinelibrary.wiley.com/doi/pdf/10.1029/2022EA002278},
note = {e2022EA002278 2022EA002278},
abstract = {Abstract Thematic map creation is a meticulous process that requires several steps to be accomplished regardless of the type of map to be produced, from data collection, through data exploitation and map publication in print, image, and GIS format. Examples are geolithological, and geomorphological maps in which most of the highest time-consuming tasks are those related to the discretization of single objects. Introducing also interpretative biases because of the different experience of the mappers in identifying a set of unique characteristics that describe those objects. In this setting, Deep Learning Computer Vision techniques could play a key role but lack the availability of a complete set of tools specific for planetary mapping. The aim of this work is to develop a comprehensive set of ready-to-use tools for landforms mapping based on validated Deep Learning methodologies and open-source libraries. We present DeepLandforms, the first pre-release of a toolset for landform mapping using Deep Learning that includes all the components for dataset preparation, model training, monitoring, and inference. In DeepLandforms, users have full access to the workflow and control over all the processes involved, granting complete control and customization capabilities. In order to validate the applicability of our tool, in this work we present the results achieved using DeepLandforms in the science case of mapping sinkhole-like landforms on Mars, as a first example that can lead us into multiple and diverse future applications.}
}



## Funding
*This study is within the Europlanet 2024 RI and EXPLORE project, and it has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 871149 and No 101004214.*
