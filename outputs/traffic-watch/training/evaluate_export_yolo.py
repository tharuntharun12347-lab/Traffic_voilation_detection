from pathlib import Path
import argparse, shutil
from ultralytics import YOLO

p = argparse.ArgumentParser(description='Evaluate on the held-out split and export a browser ONNX model')
p.add_argument('--weights', required=True)
p.add_argument('--data', required=True)
p.add_argument('--output', default='../roadwatch-yolo.onnx')
p.add_argument('--imgsz', type=int, default=512)
p.add_argument('--report', default=str(Path(__file__).with_name('model-evaluation.md')), help='Markdown metrics report path')
a = p.parse_args()

model = YOLO(a.weights)
metrics = model.val(data=a.data, split='test', imgsz=a.imgsz, workers=0, device='cpu', plots=False)
box = metrics.box
rows = ['# Held-out YOLO evaluation', '',
        f"Held-out test split. Input size: {a.imgsz}px.",
        f"Overall mAP@50: {box.map50:.3f}; mAP@50-95: {box.map:.3f}.", '',
        '| Class | Precision | Recall | mAP@50 | mAP@50-95 |', '|---|---:|---:|---:|---:|']
for index, name in model.names.items():
    rows.append(f'| {name} | {box.p[index]:.3f} | {box.r[index]:.3f} | {box.ap50[index]:.3f} | {box.ap[index].mean():.3f} |')
report = Path(a.report).resolve()
report.parent.mkdir(parents=True, exist_ok=True)
report.write_text('\n'.join(rows)+'\n', encoding='utf-8')
print('\n'.join(rows))

onnx_source = Path(model.export(format='onnx', imgsz=a.imgsz, simplify=False, nms=False))
target = Path(a.output).resolve()
target.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(onnx_source, target)
import onnx
onnx.checker.check_model(onnx.load(target))
print(f'Exported checked ONNX model: {target} ({target.stat().st_size/1024/1024:.1f} MB)')
