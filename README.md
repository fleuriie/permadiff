<div align="center">
  
# Permadiff

[![Email](https://img.shields.io/badge/EMAIL-jchoi-93BFCF?style=flat&logoSize=auto&labelColor=EEE9DA)](mailto:jchoi@mit.edu)
[![Email](https://img.shields.io/badge/EMAIL-acrantel-93BFCF?style=flat&logoSize=auto&labelColor=EEE9DA)](mailto:acrantel@mit.edu)
[![Email](https://img.shields.io/badge/EMAIL-aw4ng-93BFCF?style=flat&logoSize=auto&labelColor=EEE9DA)](mailto:aw4ng@mit.edu)

[Overview](#overview) • [Implementation](#implementation)

</div>

# Overview 🗺️

<div align="center">
  
![](imgs/running.png)

</div>

This project aims to archive the internet while using version control paradigms, primarily diffs and branches. The project is built using primarily Python 3 and was run in an x86-64 Linux development environment. The project should run cross platform. To develop locally, make sure to catch up on the dependencies:

```bash
# install dependencies from requirements.txt

pip install -r requirements.txt
```

Ideally, packages should be managed through a virtual environment. To create and use one:

```bash
# create the venv
python3 -m venv .venv

# enable the virtual environment
source ./.venv/bin/activate

# use python3 and pip as normal
```

