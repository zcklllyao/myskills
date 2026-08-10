---
name: build-paper-reports
description: Search for and download academic paper PDFs, validate file integrity, read full papers, and create one detailed source-grounded Chinese Markdown report per paper. Use for paper collection, literature review, article-by-article presentation notes, PDF-to-Markdown analysis, avoiding duplicate reports, or an end-to-end workflow that may also commit and push completed reports to a Git repository.
---

# Build Paper Reports

Turn a paper list or local PDF collection into verified PDFs and independent Chinese Markdown presentation reports. Ground every technical statement, formula, and number in the paper or an authoritative source.

## Workspace defaults

Use user-provided paths first. For this user's论文 workspace, use these defaults when no override is given:

- Workspace: `<workspace>`
- PDF directory: `<PDF directory>`
- Report repository: `<report repository>`
- Expected report remote: `<report repo remote>`

Treat the defaults as conveniences, not hard requirements. Discover the current Git branch and remote instead of assuming them.

## End-to-end workflow

### 1. Resolve the request and inventory local work

Extract the requested paper titles, aliases, desired report language/detail, PDF directory, report directory, and whether commit/push is requested. Make reasonable path assumptions when safe.

Inspect both directories before using the network:

- Match PDFs and reports by normalized title, common acronym, and filename.
- Reuse a valid local PDF.
- Skip a report only when it is an independent, substantially complete report for the same paper. A paper merely mentioned in another report does not count.
- Preserve unrelated files and dirty Git changes.

For multiple papers, maintain a small status table: `requested`, `PDF present`, `PDF valid`, `report present`, `action`, `result`.

### 2. Verify paper identity and find primary sources

When a PDF is missing, search the web for the exact paper. Prefer sources in this order:

1. Publisher or conference proceedings.
2. arXiv abstract/PDF page.
3. Official project or author/institution page.

Confirm title, authors, version, venue, year, and direct PDF URL before download. Do not silently substitute a similarly named paper. If the claimed paper cannot be verified, explain the discrepancy and stop that item instead of inventing content.

Use current authoritative sources and cite any web-supported claims in the user-facing response. Follow `references/download-strategy.md` for reliable download and fallback handling.

### 3. Download and validate PDFs

Download into the resolved PDF directory with a stable, Windows-safe filename. Never overwrite a valid local file merely to refresh it.

Use the bundled downloader when a direct PDF URL is available:

```powershell
python scripts/download_pdf.py --url "<direct-pdf-url>" --output "<paper.pdf>"
```

Then validate every candidate:

```powershell
python scripts/validate_pdfs.py "<paper.pdf>"
```

A successful HTTP request is insufficient. Reject login pages, HTML error pages, truncated files, encrypted files that cannot be read, and zero-page documents. Keep partial downloads out of the final `.pdf` path.

### 4. Read the complete paper

Read the actual PDF, not only the abstract or a search snippet. Cover all pages in manageable chunks and inspect figures/tables visually when text extraction loses layout.

Capture at least:

- Bibliographic facts and official links.
- Task definition, assumptions, inputs, and outputs.
- Motivation and gap in prior work.
- End-to-end pipeline and every major module.
- Important equations with variable meanings.
- Training data, losses, implementation, and inference procedure.
- Datasets, splits, baselines, metrics, and exact quantitative results.
- Ablations, qualitative findings, limitations, and failure cases.

Record section, page, figure, and table locations while reading. Never infer missing numbers from a plot unless clearly labeled as an estimate. Distinguish paper claims from your own analysis.

### 5. Write one independent Chinese Markdown report per paper

Read `references/report-outline.md` before drafting. Create one `.md` file per paper in the report repository unless the user requests a different layout.

Requirements:

- Make the report understandable without reading another report.
- Explain technical terms in Chinese while retaining useful English names.
- Reconstruct the method logically instead of translating paragraphs in order.
- Include exact evidence locations such as “表 2 / 第 4.3 节 / PDF 第 8 页”.
- Copy formulas only when needed and define symbols; do not fabricate equations.
- Use concise tables for comparisons, experimental results, and ablations.
- Explicitly label analysis, inference, uncertainty, and unavailable information.
- End with presentation-ready talking points and likely defense questions.
- Avoid long verbatim quotations. Paraphrase faithfully and link sources.

Use Windows-safe filenames. Prefer the canonical acronym or concise English title, for example `NeRFiller.md`.

### 6. Validate the reports

Run the bundled Markdown validator on each new or changed report:

```powershell
python scripts/validate_markdown.py "<report.md>" --min-chars 3000
```

Also inspect rendered structure and run `git diff --check` inside a Git repository. Fix replacement characters, unmatched fences/math blocks, placeholder text, heading problems, and accidental encoding damage.

Do a final evidence audit:

- Every number maps to a paper table/figure/section.
- Metadata matches an authoritative record.
- The report does not claim that a preprint is peer-reviewed without evidence.
- Limitations are paper-reported or explicitly marked as analysis.

### 7. Commit and push only when in scope

Commit/push when the user explicitly requests it or the stated workflow clearly includes repository delivery.

Before committing:

1. Check `git status --porcelain`, branch, remote, and diff.
2. Preserve unrelated user changes.
3. Stage only the reports and supporting files created for this request.
4. Use a descriptive non-interactive commit.
5. Push normally; never force-push unless explicitly authorized.
6. Verify the pushed commit and report its hash.

Do not modify global Git identity unless the user asks. Reuse existing configuration when valid.

## Failure handling

- Retry transient network failures with a different authoritative mirror or download mechanism.
- If a source serves HTML instead of PDF, delete only the task-created partial file and try the verified direct URL.
- If extraction is poor, use page rendering/OCR selectively and state any remaining uncertainty.
- If no verifiable PDF exists, produce a download-status note rather than a fake paper report.
- Continue other independent papers when one item fails.

## Completion report

Tell the user which PDFs were reused or downloaded, which reports were created or skipped, validation results, report paths, and—when requested—the commit hash and push target. Surface unresolved identity or evidence issues clearly.
