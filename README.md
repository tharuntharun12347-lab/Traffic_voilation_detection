# Traffic_voilation_detection (Roadwatch)

Roadwatch is a classroom traffic-safety demo. It runs YOLO11n in the browser on a photo or up to 30 sampled video frames and shows motorcycles, riders, helmet evidence, and possible triple riding for human review.

## Run the demo

1. Clone this repository or extract `outputs/roadwatch-website.zip`.
2. Open `outputs/traffic-watch/index.html` in a modern browser, or run `python outputs/traffic-watch/serve.py` and open the local URL it prints.
3. Select a sample or upload an image/video, then start the scan.

The standalone page embeds the current browser model and app code. An internet connection is used to load ONNX Runtime Web; uploaded media and inference stay in the browser.

## Project structure

```text
outputs/
  traffic-watch/                 Browser app, model, samples, and training source
    training/                    Conversion, training, evaluation, and packaging scripts
      README.md                   Reproducible training/release guide
  roadwatch-website.zip           Shareable standalone website
  .roadwatch-training/            Local dataset conversions, runs, and checkpoints (not committed)
work/, runs/, Ultralytics/         Local runtime and training artifacts (not committed)
```

The dataset and training checkpoints are excluded from Git. Code and instructions to prepare data, train, evaluate, and rebuild are in `outputs/traffic-watch/training/`.

## Current model

The current browser model was fine-tuned from `yolo11n.pt` for 8 epochs on all 4,644 training images, using 512px images and batch size 8 on CPU. The 117-image validation split was used during training; the separate 78-image test split was reserved for final evaluation. Held-out mAP@50 is **0.884** (previous model: 0.768). See [`model-evaluation.md`](outputs/traffic-watch/training/model-evaluation.md) for per-class results and the comparison.

## Dataset credit and limits

Traffic Rule Violation Detection Dataset in Dhaka Urban Traffic Environment, v1. Authors: Ashesh Bar, Manobendra Biswas, Abir Hasan, Marufur Rahman Mithu, Faisal Ahmad, and Tonmoy Das. Mendeley Data, DOI [10.17632/ycv2mbph4b.1](https://doi.org/10.17632/ycv2mbph4b.1), licensed CC BY-NC 4.0. The dataset and derived model are for non-commercial use under the applicable terms unless separate permission is obtained. Preserve attribution when sharing.

The data contains labeled images, not labeled videos. The demo can sample uploaded videos for inference, but it has no temporal training. Red-light crossing is not assessed. Results are preliminary; the detector can miss or miscount unseen examples. A missing alert does not establish that a violation did not occur, so review the original media.

See the [training and release guide](outputs/traffic-watch/training/README.md) for setup and GitHub instructions.
