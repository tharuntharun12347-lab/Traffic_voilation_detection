# Model artifacts

- `roadwatch-yolo.onnx` is the browser inference model used by `frontend/` and the demo.
- `weights/best.pt` is the checkpoint from the documented eight-epoch YOLO11n fine-tune.
- `classes.yaml` records the five output labels in model order.

The fine-tune used the Mendeley Traffic Rule Violation Detection Dataset in Dhaka Urban Traffic Environment (v1), by Ashesh Bar, Manobendra Biswas, Abir Hasan, Marufur Rahman Mithu, Faisal Ahmad, and Tonmoy Das, DOI [10.17632/ycv2mbph4b.1](https://doi.org/10.17632/ycv2mbph4b.1), CC BY-NC 4.0. The dataset and derived model are for non-commercial use under the applicable license terms unless separate permission is obtained. Preserve attribution when sharing.

The checkpoint is about 5.45 MB; the ONNX model is about 10.5 MB. Both are below GitHub's 100 MB per-file limit. Downloaded source data and training caches are not included.
