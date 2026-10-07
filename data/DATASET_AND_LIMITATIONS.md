# Dataset attribution and handling

This repository includes the prepared YOLO-format images and annotations under `data/processed/yolo-data/`. The original dataset is **Traffic Rule Violation Detection Dataset in Dhaka Urban Traffic Environment, v1**, by Ashesh Bar, Manobendra Biswas, Abir Hasan, Marufur Rahman Mithu, Faisal Ahmad, and Tonmoy Das. Mendeley Data, [DOI 10.17632/ycv2mbph4b.1](https://doi.org/10.17632/ycv2mbph4b.1). License: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

The included converted data is redistributed under the source dataset's license. Give attribution, link to the license, and indicate if changes were made. The license is noncommercial; obtain separate permission before commercial use of the dataset or derived model. This folder contains labeled images, not labeled videos. The 78-image test split is held out and must not be used for training or checkpoint selection.

Image files use Git LFS. After cloning, install Git LFS and fetch the image contents:

```bash
git lfs install
git lfs pull
```

Dataset layout:

- `images/train`, `labels/train`: 4,644 training images and labels
- `images/valid`, `labels/valid`: 117 validation images and labels
- `images/test`, `labels/test`: 78 held-out test images and labels
- `traffic.yaml`: relative-path YOLO configuration
