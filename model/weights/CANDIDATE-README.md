# Experimental candidate checkpoint

`roadwatch-yolo11n-640-epoch1-interrupted-candidate.pt` is an experimental checkpoint created by fine-tuning the released RoadWatch YOLO11n model at 640 px. The requested 12-epoch run was stopped during epoch 2, so this checkpoint reflects the best completed validation at epoch 1 only.

Epoch 1 validation on the 117-image validation split: precision 0.860, recall 0.865, mAP50 0.896, mAP50-95 0.462. These results do not establish performance on the independent 78-image test split; the candidate has not been evaluated there. Do not treat it as the production model.

`best.pt` remains the released model used by the project. The candidate is stored separately for continued development and comparison.
