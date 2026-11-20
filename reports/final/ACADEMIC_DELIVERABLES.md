# Academic deliverables and reproduction

- [One-page final report](RETAILASSIST_FINAL_REPORT.pdf) and [editable report source](RETAILASSIST_FINAL_REPORT.md).
- [12-slide PDF presentation](RETAILASSIST_PRESENTATION.pdf), landscape16:9, using Client X and actual measurements.
- render_report.py creates the one-page report; render_slides.py creates the presentation.
- academic-requirements.txt contains offline authoring dependencies, separate from inference.

The former Markdown slide deck was removed at the student's request and replaced by the PDF. Its original is privately preserved outside the repository. The one-page report remains a separate unchanged deliverable.

From repository root:

```bash
python3.12 -m venv /tmp/retailassist-report-env
source /tmp/retailassist-report-env/bin/activate
python -m pip install -r reports/final/academic-requirements.txt
python reports/final/render_report.py
python reports/final/render_slides.py
pdfinfo reports/final/RETAILASSIST_FINAL_REPORT.pdf
pdfinfo reports/final/RETAILASSIST_PRESENTATION.pdf
```

Expected: report1page; presentation12pages. Both PDF files were rendered and visually checked. Poppler supplies pdfinfo/pdftoppm; install it separately if unavailable. The presentation uses measured plots under evaluation/; no identifying screenshots are included. Current local tests and CI are distinguished from historical production outcomes. Ranking-effectiveness metrics and semantic comparisons remain outstanding. No PPTX is required for the requested PDF presentation.
