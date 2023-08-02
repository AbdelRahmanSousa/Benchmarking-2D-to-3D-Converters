# Project: Benchmarking 2D To 3D Converters 

## Service: Floor Plan 3D Converter

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) 
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
  

### Description: 

- A dashboard that allows user to upload 2D floor plan and 2D devices, it then converts both the floor 
  plan and devices to their corresponding 3D shape.

### Requirements 

- Python 3.11+
- Pix2Vox [pretrained model](https://gateway.infinitescript.com/s/Pix2Vox-A-ShapeNet.pth) and place it in '/pretrained_models/Pix2Vox'

### Contents 

The project have a structure as below: 

  

```bash 

├── Benchmarking-2D-to-3D-Converters

│   ├── dashboard.py 

``` 

*  Main Files Description 

`dashboard.py` the main dashboard that allows the user to upload a 2D floor plan and place devices in it. 

Example 

```bash 

python dashboard.py 

``` 


### List of Arguments accepted for the main function 

  NONE

### Results 

- a web based dashboard that can convert both floorplans and models

  

#### Deployment  

- The dashboard is deployed on a local server
