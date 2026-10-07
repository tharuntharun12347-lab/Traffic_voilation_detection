"""Build a compact training subset that deliberately contains triple-riding examples."""
import argparse, random, re, shutil
from collections import defaultdict
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--data-root', required=True, help='Converted YOLO dataset root')
p.add_argument('--output', required=True, help='New subset output folder')
p.add_argument('--triple-groups', type=int, default=250)
p.add_argument('--other-groups', type=int, default=200)
a = p.parse_args()
src, out = Path(a.data_root).resolve(), Path(a.output).resolve()
rng = random.Random(42)
groups = defaultdict(list)
images_by_stem = {
    image.stem: image
    for image in (src/'images'/'train').iterdir()
    if image.is_file()
}
for label in sorted((src/'labels'/'train').glob('*.txt')):
    match = re.match(r'(Image\d+)', label.stem)
    group = match.group(1) if match else label.stem
    classes = {int(line.split()[0]) for line in label.read_text(encoding='utf-8').splitlines() if line.strip()}
    image = images_by_stem.get(label.stem)
    if image: groups[group].append((image, label, classes))

triple = [g for g, rows in groups.items() if any(4 in row[2] for row in rows)]
other = [g for g, rows in groups.items() if not any(4 in row[2] for row in rows)]
rng.shuffle(triple); rng.shuffle(other)
chosen = []
for pool, count, must_contain in ((triple, a.triple_groups, True), (other, a.other_groups, False)):
    if len(pool) < count: raise ValueError(f'Need {count} groups, only found {len(pool)}')
    chosen.extend((g, must_contain) for g in pool[:count])

train_images = out/'images'/'train'; train_labels = out/'labels'/'train'
train_images.mkdir(parents=True, exist_ok=True); train_labels.mkdir(parents=True, exist_ok=True)
for i, (group, must_contain) in enumerate(chosen):
    rows = groups[group]
    candidates = [row for row in rows if (4 in row[2]) == must_contain]
    image, label, _ = rng.choice(candidates or rows)
    target_stem = f'{group}_{i:04d}'
    shutil.copy2(image, train_images/(target_stem+image.suffix.lower()))
    shutil.copy2(label, train_labels/(target_stem+'.txt'))

yaml = '\n'.join([
    f'path: {out.as_posix()}', 'train: images/train',
    f'val: {(src/"images"/"valid").as_posix()}',
    f'test: {(src/"images"/"test").as_posix()}', 'names:',
    '  0: motorcycle', '  1: helmet_on', '  2: no_helmet',
    '  3: rider', '  4: triple_riding', ''])
(out/'traffic.yaml').write_text(yaml, encoding='utf-8')
print(f'Wrote {len(chosen)} group representatives ({a.triple_groups} with triple-riding labels) to {out}')
print(out/'traffic.yaml')
