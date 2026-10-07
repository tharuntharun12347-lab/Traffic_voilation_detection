"""Add the measured test report and validation learning curve to index.html."""
from __future__ import annotations

import argparse
import csv
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = Path("runs/detect/work/runs/roadwatch-retrained-600-20261005/results.csv")
DISPLAY = {
    "motorcycle": "Motorcycle",
    "helmet_on": "Helmet worn",
    "no_helmet": "Possible no helmet",
    "rider": "Rider",
    "triple_riding": "Triple riding",
}


def parse_evaluation(path: Path) -> tuple[float, float, list[dict[str, float | str]]]:
    content = path.read_text(encoding="utf-8")
    overall = re.search(r"Overall mAP@50:\s*([0-9]+(?:\.[0-9]+)?);\s*mAP@50-95:\s*([0-9]+(?:\.[0-9]+)?)", content)
    if not overall:
        raise ValueError(f"No overall test metrics found in {path}")
    rows: list[dict[str, float | str]] = []
    for line in content.splitlines():
        match = re.match(r"\|\s*([a-z_]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|", line)
        if match:
            name, precision, recall, ap50, ap = match.groups()
            rows.append({
                "key": name,
                "name": DISPLAY.get(name, name.replace("_", " ").title()),
                "precision": float(precision),
                "recall": float(recall),
                "ap50": float(ap50),
                "ap": float(ap),
            })
    if len(rows) != 5:
        raise ValueError(f"Expected five class rows in {path}, found {len(rows)}")
    return float(overall.group(1)), float(overall.group(2)), rows


def learning_curve(path: Path) -> tuple[list[float], str]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    values = [float(row["metrics/mAP50(B)"]) for row in rows]
    if not values:
        raise ValueError(f"No validation history found in {path}")
    width, height, left, right, top, bottom = 700, 205, 44, 16, 16, 35
    chart_w, chart_h = width - left - right, height - top - bottom
    points = [
        (left + i * chart_w / max(1, len(values) - 1), top + (1 - value) * chart_h)
        for i, value in enumerate(values)
    ]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"{left},{top + chart_h} {poly} {points[-1][0]:.1f},{top + chart_h}"
    lines = []
    for value in (0, 0.5, 1):
        y = top + (1 - value) * chart_h
        lines.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="chart-grid"/>'
            f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end">{value:.1f}</text>'
        )
    circles = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="chart-point"><title>Epoch {i+1}: mAP@50 {values[i]:.3f}</title></circle>'
        for i, (x, y) in enumerate(points)
    )
    labels = []
    for i, (x, _) in enumerate(points):
        if len(values) <= 10 or i in {0, len(values)-1} or i % 2 == 0:
            labels.append(f'<text x="{x:.1f}" y="{height-7}" text-anchor="middle">{i+1}</text>')
    svg = (
        f'<svg class="learning-svg" viewBox="0 0 {width} {height}" role="img" aria-label="Validation mAP at 50 across {len(values)} training epochs">'
        + "".join(lines)
        + f'<polygon points="{area}" class="chart-area"/><polyline points="{poly}" class="chart-line"/>'
        + circles + "".join(labels) + "</svg>"
    )
    return values, svg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluation", type=Path, default=ROOT / "training" / "model-evaluation.md")
    parser.add_argument("--history", type=Path, default=Path.cwd() / DEFAULT_RUN)
    args = parser.parse_args()

    map50, map95, classes = parse_evaluation(args.evaluation)
    history, svg = learning_curve(args.history)
    body = []
    for row in classes:
        name = html.escape(str(row["name"]))
        ap = float(row["ap50"])
        body.append(
            '<div class="bench-row">'
            f'<div class="bench-label">{name}<small>AP@50</small></div>'
            f'<div class="bench-meter" role="img" aria-label="{name} AP at 50 {ap:.1%}"><span style="width:{ap*100:.1f}%"></span></div>'
            f'<strong>{ap:.1%}</strong><div class="bench-pr">P {float(row["precision"]):.1%} · R {float(row["recall"]):.1%}</div>'
            '</div>'
        )
    panel = f'''<section class="benchmark" id="results">
<div class="cap-heading"><div><div class="cap-kicker">Independent model check · 78 held-out images</div><h2>Measured on frames the model never trained on.</h2></div><p>Test-set results, reported per class. Scores describe this dataset and camera style; they are not guarantees for new footage.</p></div>
<div class="benchmark-grid"><article class="benchmark-score"><div class="score-ring" style="--score:{map50*100:.1f}%"><div><strong>{map50:.1%}</strong><span>mAP@50</span></div></div><div class="score-caption">Across all five detection labels</div><div class="score-secondary"><span>mAP@50–95</span><b>{map95:.1%}</b></div><div class="score-secondary"><span>Test frame size</span><b>512 px</b></div></article>
<article class="benchmark-classes"><div class="benchmark-table-head"><span>Detection class</span><span>AP@50</span><span>Precision · recall</span></div>{''.join(body)}</article></div>
<article class="learning-card"><div class="learning-head"><div><div class="cap-kicker">Training trace · validation split</div><h3>Detection quality improved over the fine-tune.</h3></div><span>117 validation images · {len(history)} epochs</span></div>{svg}</article>
<div class="review-note"><div class="review-note-mark">i</div><div><strong>How to read this score</strong><span>mAP measures box quality and class ranking at a chosen overlap threshold; it is not a percentage of frames classified correctly. The browser requires a 35% triple-riding confidence cue; on the held-out test split that cutoff gave 94.4% precision and 89.4% recall for that class. The test sample is small, and no alert does not rule out a violation.</span></div></div>
</section>'''

    index = ROOT / "index.html"
    page = index.read_text(encoding="utf-8")
    style_block = re.search(r'<style id="roadwatch-presentation">(.*?)</style>', page, re.DOTALL)
    if not style_block:
        raise RuntimeError("Presentation stylesheet is missing")
    css = '''
.benchmark{margin-top:58px}.benchmark-grid{display:grid;grid-template-columns:220px minmax(0,1fr);gap:14px}.benchmark-score,.benchmark-classes,.learning-card{border:1px solid #263f36;border-radius:16px;background:linear-gradient(150deg,#11231f,#0c1916);padding:19px}.benchmark-score{display:flex;flex-direction:column;align-items:center;justify-content:center}.score-ring{width:132px;height:132px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--lime) var(--score),#293d34 0);position:relative}.score-ring:before{content:"";position:absolute;inset:8px;border-radius:50%;background:#10201b}.score-ring>div{position:relative;text-align:center}.score-ring strong{font-size:34px;letter-spacing:-.06em;display:block}.score-ring span{font-size:9px;text-transform:uppercase;letter-spacing:.12em;color:#9bb1a4}.score-caption{margin:13px 0 15px;color:#9db1a5;font-size:10px;text-align:center}.score-secondary{display:flex;justify-content:space-between;width:100%;padding:9px 0;border-top:1px solid #ffffff10;font-size:10px;color:#91a69b}.score-secondary b{color:#e3eee6}.benchmark-table-head,.bench-row{display:grid;grid-template-columns:minmax(120px,1fr) minmax(100px,1.3fr) 58px minmax(115px,.9fr);align-items:center;gap:12px}.benchmark-table-head{font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:#71877b;padding:2px 3px 11px}.benchmark-table-head span:nth-child(2){grid-column:2/4}.benchmark-table-head span:nth-child(3){grid-column:4}.bench-row{border-top:1px solid #ffffff0b;padding:12px 3px}.bench-label{font-size:11px;font-weight:650}.bench-label small{display:block;color:#71877b;font-size:9px;font-weight:450;margin-top:2px}.bench-meter{height:7px;border-radius:99px;background:#263b33;overflow:hidden}.bench-meter span{height:100%;display:block;border-radius:99px;background:linear-gradient(90deg,#7cd9ad,var(--lime))}.bench-row>strong{font-size:11px;text-align:right}.bench-pr{font-size:9px;color:#8da398;text-align:right}.learning-card{margin-top:14px}.learning-head{display:flex;justify-content:space-between;align-items:end;gap:16px}.learning-head h3{font-size:14px;margin:7px 0 0;letter-spacing:-.025em}.learning-head>span{font-size:9px;color:#7f9589;white-space:nowrap}.learning-svg{display:block;width:100%;height:auto;margin-top:12px;overflow:visible}.learning-svg text{font:10px ui-sans-serif,system-ui,sans-serif;fill:#82988c}.chart-grid{stroke:#ffffff12;stroke-width:1;stroke-dasharray:3 5}.chart-area{fill:url(#chartFill);fill:#c4f36b14}.chart-line{fill:none;stroke:#c9ff70;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}.chart-point{fill:#d6ff8b;stroke:#13241e;stroke-width:2}.benchmark .review-note{margin-top:14px}
@media(max-width:760px){.benchmark-grid{grid-template-columns:1fr}.benchmark-score{display:grid;grid-template-columns:140px 1fr;justify-items:start;column-gap:12px}.score-ring{grid-row:span 3}.score-caption{margin:0 0 10px;text-align:left;align-self:end}.score-secondary{max-width:240px}.benchmark-table-head,.bench-row{grid-template-columns:minmax(100px,1fr) minmax(70px,1fr) 44px minmax(98px,.9fr);gap:8px}.learning-head{display:block}.learning-head>span{display:block;margin-top:7px}}
@media(max-width:420px){.benchmark-classes{padding:13px}.benchmark-table-head,.bench-row{grid-template-columns:minmax(86px,1fr) minmax(56px,.8fr) 38px minmax(88px,.9fr);gap:6px}.bench-label{font-size:10px}.bench-pr{font-size:8px}.benchmark-score{grid-template-columns:118px 1fr;padding:14px}.score-ring{width:112px;height:112px}.score-ring strong{font-size:28px}}
'''
    style_content = style_block.group(1)
    style_content = re.sub(r"/\* roadwatch-benchmark-styles \*/.*$", "", style_content, flags=re.DOTALL)
    page = page[:style_block.start(1)] + style_content + "/* roadwatch-benchmark-styles */\n" + css + page[style_block.end(1):]
    marker = '<section class="benchmark" id="results">'
    start, end = page.find(marker), page.find('<footer class="footer">')
    if start >= 0 and end > start:
        page = page[:start] + panel + page[end:]
    elif end >= 0:
        page = page[:end] + panel + page[end:]
    else:
        raise RuntimeError("Could not place the benchmark panel before the page footer")
    index.write_text(page, encoding="utf-8")
    print(f"Added held-out metrics and {len(history)}-epoch validation chart to {index}")


if __name__ == "__main__":
    main()
