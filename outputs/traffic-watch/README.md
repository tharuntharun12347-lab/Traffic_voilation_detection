# Roadwatch · Traffic Safety Vision

Roadwatch is a browser-based YOLO11n prototype for reviewing traffic photos or sampled video frames. It highlights motorcycles, riders, helmet evidence, and possible triple riding; a person reviews the original media.

## Run the demo

1. Extract `roadwatch-website.zip` or clone the repository.
2. Open `traffic-watch/index.html` in Chrome or another modern browser. The standalone page is self-contained.
3. Choose a sample or upload a JPG, PNG, WEBP, MP4, WEBM, or MOV file, then run the scan.

Video input samples up to 30 frames and reports their timestamps. The bundled sample clip is a montage of still photos, not continuous traffic footage. ONNX Runtime Web loads from a CDN; inference and uploaded media stay in the browser.

## Current model and measured results

The current browser model started from pretrained `yolo11n.pt` and was fine-tuned on all 4,644 training images for 8 epochs at 512px and batch size 8 on CPU. Training used the separate 117-image validation split; the 78-image held-out test split was reserved for final evaluation.

Held-out mAP@50 improved from **0.768 to 0.884**. AP@50 improved for all five labels. At the browser's 0.35 triple-riding alert cutoff, test precision was **94.4%** and recall was **89.4%**. Full metrics and the baseline comparison are in `training/model-evaluation.md`; the page shows class scores and the validation learning curve.

## Reproduction

Follow [`training/README.md`](training/README.md) to prepare the separately downloaded dataset, retrain, evaluate, and rebuild the standalone page and website ZIP. The dataset and model are restricted to non-commercial use under the source terms; keep the attribution below when sharing.

## Dataset credit and limitations

Traffic Rule Violation Detection Dataset in Dhaka Urban Traffic Environment, v1. Authors: Ashesh Bar, Manobendra Biswas, Abir Hasan, Marufur Rahman Mithu, Faisal Ahmad, and Tonmoy Das. Mendeley Data, DOI [10.17632/ycv2mbph4b.1](https://doi.org/10.17632/ycv2mbph4b.1), CC BY-NC 4.0.

This is a small preliminary evaluation on 78 held-out images. Object-detection metrics are not percentages of correct real-world decisions. The model can miss or miscount unseen examples and can associate helmet evidence incorrectly; have a person check every result. The data labels images, not videos. Red-light crossing is not assessed, and sampled still frames cannot establish that a vehicle crossed on a red signal.
