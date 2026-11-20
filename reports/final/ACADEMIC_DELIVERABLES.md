# Academic deliverables and reproduction

- `RETAILASSIST_FINAL_REPORT.md`: editable, evidence-based academic source.
- `RETAILASSIST_FINAL_REPORT.pdf`: exactly one-page final report PDF with fresh anonymized local measurements.
- `PRESENTATION.md`: complete editable 12-slide defense content and speaker notes. This is not a PPTX; the mandated artifact-tool loader was unavailable, so the brief's editable-content fallback was used.
- `render_report.py`: PDF renderer. It consumes the Markdown source and genuine PNG figures under `evaluation/`.
- `academic-requirements.txt`: offline-only authoring dependencies, separate from inference.

From the repository root, to rebuild the PDF after reviewing evidence:

```bash
python3.12 -m venv /tmp/retailassist-report-env
source /tmp/retailassist-report-env/bin/activate
python -m pip install -r reports/final/academic-requirements.txt
python reports/final/render_report.py
mkdir -p /tmp/retailassist-report-review
pdftoppm -scale-to 1200 -png reports/final/RETAILASSIST_FINAL_REPORT.pdf /tmp/retailassist-report-review/page
```

Inspect every rendered page before submission. Poppler supplies pdftoppm (on macOS, install separately with Homebrew if absent). PDF metadata timestamps reflect the actual authoring environment; the report's evidence date is in Africa/Nairobi time. The report does not contain invented ranking metrics or semantic results. The report is intentionally exactly one page, as requested. Extended technical discussion belongs in README/evaluation documentation, not another final report. The earlier pre-anonymization presentation MVP was READY WITH LIMITATIONS after authorized repair and controlled public checks. Those observations are historical; the current anonymized deployment needs its own live checks. The one-page report uses concise measurements rather than embedded figures. Current Client X plots are available under evaluation/; identifying screenshots are excluded.

To prepare slides in PowerPoint, use the 12 numbered sections of PRESENTATION.md, keep the speaker notes, and insert only newly verified Client X figures. Do not replace missing relevance metrics with illustrative scores. No PowerPoint file was exported or inspected in PowerPoint during this task.
