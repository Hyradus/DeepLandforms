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

* 25 GB of free disk space
* Ubuntu OS or other distro
* Docker
* Nvidia-docker
* Nvidia GPU
* 16GB RAM (more is better, especially when processing very high-resolution images)
* 8+ cpu cores

## Tutorial

See the tutorial folder.

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

* [ ] Remove nvidia-docker strict requirement
* [ ] Remove Detectron2 and make it optional
* [ ] Implement additional architectures (e.g. U-Net, YOLO)

## Funding
*This study is within the Europlanet 2024 RI and EXPLORE project, and it has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No 871149 and No 101004214.*
