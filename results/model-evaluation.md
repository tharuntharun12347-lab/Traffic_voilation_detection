# Held-out YOLO evaluation

Full-data YOLO11n fine-tune. Test split: 78 images and 497 instances, held out from training and checkpoint selection. Input size: 512px. Training used all 4,644 training images for 8 epochs; validation used the separate 117-image split.

Overall mAP@50: 0.884; mAP@50-95: 0.472. Previous bundled model: mAP@50 0.768; mAP@50-95 0.385.

| Class | Precision | Recall | mAP@50 | mAP@50-95 |
|---|---:|---:|---:|---:|
| motorcycle | 0.950 | 0.937 | 0.967 | 0.687 |
| helmet_on | 0.837 | 0.689 | 0.834 | 0.368 |
| no_helmet | 0.866 | 0.762 | 0.849 | 0.388 |
| rider | 0.808 | 0.752 | 0.813 | 0.372 |
| triple_riding | 0.944 | 0.894 | 0.959 | 0.548 |

At the browser's fixed 0.35 triple-riding confidence cutoff, held-out test precision was 0.944 and recall was 0.894.

| Class | Previous AP@50 | Full-data AP@50 | Change |
|---|---:|---:|---:|
| motorcycle | 0.942 | 0.967 | +0.025 |
| helmet_on | 0.683 | 0.834 | +0.151 |
| no_helmet | 0.739 | 0.849 | +0.110 |
| rider | 0.591 | 0.813 | +0.222 |
| triple_riding | 0.883 | 0.959 | +0.076 |

This is a preliminary result on a small 78-image test sample; scores are not guarantees for unfamiliar media. The dataset is CC BY-NC 4.0. See `DATASET_AND_LIMITATIONS.md` for attribution and limitations. The dataset contains labeled images, not labeled videos; red-light crossing is not assessed.
