"""Manual report/chart material generation from actual evaluation files; no execution by agent."""
import argparse
import csv
import html
import json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--results', required=True); parser.add_argument('--output', required=True); args = parser.parse_args()
    directory = Path(args.results)
    if not (directory / 'retrieval.csv').exists(): parser.error('Actual retrieval.csv is absent. Do not fabricate report values.')
    rows = list(csv.DictReader((directory / 'retrieval.csv').open()))
    metadata = json.loads((directory / 'metadata.json').read_text())
    bars = []
    for method in sorted({r['method'] for r in rows}):
        values = [float(r['ndcg_at_k']) for r in rows if r['method'] == method and r['split'] == 'test' and r['ndcg_at_k']]
        if values:
            mean = sum(values) / len(values)
            bars.append(f'<p>{html.escape(method)} — NDCG@K {mean:.3f} ({len(values)} scored test queries)</p><div style="height:18px;background:#e5eddf"><div style="height:100%;width:{mean*100:.2f}%;background:#295343"></div></div>')
    document = '<!doctype html><meta charset="utf-8"><title>Actual MVP evaluation</title><main style="max-width:850px;margin:50px auto;font:16px/1.8 system-ui;color:#243d32"><h1>Actual RetailAssist MVP evaluation</h1><p>Generated from student-executed results. No historical Flipkart scores reused.</p>' + ''.join(bars) + '<pre>' + html.escape(json.dumps(metadata, indent=2)) + '</pre><p>Unsupported-claim rate remains pending human review. Paste these measured outputs into research/mvp/report_draft.md, explain limitations, and export the reviewed final report to PDF.</p></main>'
    Path(args.output).write_text(document)
    print('Created an HTML evidence sheet from actual result files. Review before PDF export.')
if __name__ == '__main__': main()
