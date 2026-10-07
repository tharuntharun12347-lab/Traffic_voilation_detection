# Dataset, training, evaluation, and limitations

## Dataset and license

Source: **Traffic Rule Violation Detection Dataset in Dhaka Urban Traffic Environment**, Mendeley Data v1, DOI [10.17632/ycv2mbph4b.1](https://doi.org/10.17632/ycv2mbph4b.1). Authors: Ashesh Bar, Manobendra Biswas, Abir Hasan, Marufur Rahman Mithu, Faisal Ahmad, and Tonmoy Das. The source uses a CC BY-NC 4.0 license. Attribute the authors and dataset, and do not use the dataset or derived model commercially without separate permission.

The augmented data contains 4,644 training images, 117 validation images, and a separate 78-image test set (497 labeled instances). The five COCO classes are Bike, Helmet_On, No_helmet, Rider, and Trippling; `prepare_yolo_data.py` maps them to `motorcycle`, `helmet_on`, `no_helmet`, `rider`, and `triple_riding`. The repository does not include the source or converted dataset files.

## Full-data retraining and held-out evaluation

A fresh YOLO11n fine-tune started from pretrained `yolo11n.pt` and used all 4,644 training images for 8 epochs, 512px input size, batch 8, and CPU execution. Seed 42 and the augmentations configured in `train_yolo.py` were used. Training-time validation used only the 117-image validation split. The held-out test split was not used for training or checkpoint selection.

Compared with the previously bundled model, the full-data model improved mAP@50 from 0.768 to 0.884 and mAP@50-95 from 0.385 to 0.472. AP@50 improved in all five classes:

| Detection class | Previous AP@50 | Full-data AP@50 | Change |
|---|---:|---:|---:|
| Motorcycle | 0.942 | 0.967 | +0.025 |
| Helmet worn | 0.683 | 0.834 | +0.151 |
| Possible no helmet | 0.739 | 0.849 | +0.110 |
| Rider | 0.591 | 0.813 | +0.222 |
| Triple riding | 0.883 | 0.959 | +0.076 |

At the browser's fixed 0.35 triple-riding confidence cutoff, test precision was 0.944 and recall was 0.894. This threshold is a practical alert setting, not a guarantee. Full precision, recall, AP, and the training trace are in `model-evaluation.md` and the website performance panel.

The held-out test set has only 78 images, so its results are preliminary and have substantial sampling uncertainty. Metrics measure box quality and ranking on this dataset; they are not percentages of correct real-world decisions and may not transfer to new roads, cameras, or weather.

## Reproduction

See `README.md` in this directory for the complete environment setup and commands. In brief: convert the source COCO annotations with `prepare_yolo_data.py`, train with `train_yolo.py`, evaluate the untouched test split with `evaluate_export_yolo.py`, then update the panel and rebuild with `package_browser_demo.py` followed by `build_release.py`. Export candidate models to a temporary path and compare per-class results before replacing the browser model.

## Limits and appropriate use

The classes represent visual boxes, not event-level legal decisions. The model can miss or double-count objects on unseen images. Helmet evidence can be occluded or associated with the wrong rider. A missing detection does not prove compliance; a human should review every result.

The source contains labeled images, not labeled videos. Uploaded video is sampled for inference only; there is no temporal training or tracking. The demo samples up to 30 frames, so activity between samples can be missed. Its sample clip is a lightly animated montage of still photographs, not continuous traffic footage.

The dataset has no signal-state or stop-line labels. Red-light crossing is not assessed. Establishing a signal violation would require suitable video, signal and stop-line recognition, calibrated geometry, temporal tracking, and separate training and evaluation footage. This prototype is for classroom demonstration only.
