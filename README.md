# AI Certification Landscape

An offline, reproducible data science project exploring the structure, prices and disclosures of AI credentials, with an explainable TF-IDF similarity experiment.

## Start here

Open `notebooks/01_landscape.ipynb` for the executed analysis, tables and charts. Raw source data is bundled, so running the project does not require network access after dependencies are installed.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/analysis.py
python src/analysis.py --query "generative AI developer professional"
python -m unittest discover -s tests -v
```

Run these commands from this project directory. Open the notebook in VS Code or a Jupyter environment using the same Python environment. Notebook execution requires a working Python kernel.

## Research questions

- Which issuers, tiers and credential types appear in this catalog?
- Which facts are most often undisclosed?
- How do price options vary within currency, billing, label and tax groups?
- Can a transparent lexical similarity method retrieve related credentials?

## Project structure

- `data/raw/`: original upstream JSON, README and data license.
- `src/analysis.py`: validation, normalization, summaries, SVG charts and TF-IDF retrieval.
- `notebooks/01_landscape.ipynb`: executed exploratory analysis and interpretation.
- `results/`: normalized tables, price summaries, missingness, source checksum and charts.
- `tests/`: checks for nested-table grain, null preservation and retrieval behavior.

## Snapshot findings

The bundled dataset is dated **2026-11-01**. It contains **77 credentials from 22 issuers**, including **65 active** records. **59 credentials** disclose at least one price, producing **76 price rows**. These describe the bundled catalog, not the entire AI education market.

## Methodology and limits

Null means “not stated by the issuer,” never zero or free. Credentials and price options have different table grains. Price summaries group currency, billing, label and tax; regional conditions remain in the detailed table. They are descriptive distributions of listed options, not a value ranking. All-status summaries include retired and announced credentials; retrieval defaults to active records. The raw JSON preserves nested structures and original date precision; list fields in the credential CSV are JSON strings.

There are no salary, completion, pass-rate, demand or independent quality labels. Accordingly this project does not claim career ROI or train an outcome predictor. Retrieval scores measure text similarity; no labeled relevance evaluation has yet been performed. Missingness is disclosure analysis, not a provider-quality score. Facts may have changed since the snapshot.

## Provenance and attribution

Source: [Jake Boland's AI certifications dataset](https://github.com/jakeboland/ai-certifications-dataset). Canonical publisher: **[AI Course Check (aicoursecheck.com)](https://aicoursecheck.com/data/)**. Data license: **CC BY 4.0**; full text is preserved at `data/raw/LICENSE`. See `CITATION.cff` for the upstream citation.

The raw files were retrieved from the upstream main branch on 2026-11-12. `results/summary.json` records the bundled JSON's SHA-256 for reproducibility. The raw file is unchanged in substance; processed tables, disclosure indicators and similarity scores are adaptations created for this project. No issuer facts have been independently reverified. To update, replace the raw JSON with a compatible upstream snapshot and rerun the pipeline and notebook; do not silently mix snapshots.
