from pathlib import Path
import argparse, json, shutil

CLASSES=['Bike','Helmet_On','No_helmet','Rider','Trippling']
DISPLAY=['motorcycle','helmet_on','no_helmet','rider','triple_riding']
p=argparse.ArgumentParser(description='Convert the dataset COCO boxes to YOLO labels')
p.add_argument('--dataset-root',required=True,help='Folder containing train/, valid/, test/ with COCO annotations')
p.add_argument('--output',default='yolo-data')
a=p.parse_args(); src=Path(a.dataset_root).resolve(); out=Path(a.output).resolve(); mapping={n:i for i,n in enumerate(CLASSES)}
for split in ('train','valid','test'):
    folder=src/split; coco=json.loads((folder/'_annotations.coco.json').read_text(encoding='utf-8'))
    cats={c['id']:c['name'] for c in coco['categories']}; imgs={i['id']:i for i in coco['images']}; anns={i['id']:[] for i in coco['images']}
    for ann in coco['annotations']:
        cls=mapping.get(cats.get(ann['category_id']))
        if cls is None: continue
        x,y,w,h=ann['bbox']; iw=float(imgs[ann['image_id']]['width']); ih=float(imgs[ann['image_id']]['height'])
        x1=max(0,min(iw,x)); y1=max(0,min(ih,y)); x2=max(x1,min(iw,x+w)); y2=max(y1,min(ih,y+h))
        if x2>x1 and y2>y1: anns[ann['image_id']].append((cls,(x1+x2)/2/iw,(y1+y2)/2/ih,(x2-x1)/iw,(y2-y1)/ih))
    (out/'images'/split).mkdir(parents=True,exist_ok=True); (out/'labels'/split).mkdir(parents=True,exist_ok=True)
    for img in coco['images']:
        origin=folder/img['file_name']; target=out/'images'/split/img['file_name']
        if origin.exists() and not target.exists(): shutil.copy2(origin,target)
        if not target.exists(): raise FileNotFoundError(origin)
        txt=''.join(f'{c} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n' for c,cx,cy,w,h in anns[img['id']])
        (out/'labels'/split/(Path(img['file_name']).stem+'.txt')).write_text(txt,encoding='utf-8')
yaml='\n'.join(['path: '+out.as_posix(),'train: images/train','val: images/valid','test: images/test','names:']+[f'  {i}: {n}' for i,n in enumerate(DISPLAY)])+'\n'
(out/'traffic.yaml').write_text(yaml,encoding='utf-8'); print(out/'traffic.yaml')
