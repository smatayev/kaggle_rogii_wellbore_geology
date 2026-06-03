# kaggle_rogii_wellbore_geology

Kaggle featured ROGII - Wellbore Geology Prediction. Building a model that contributes to automating drilling operations in the oil and gas industry.

## Visualization Dashboard

This repository includes an interactive Streamlit app for exploring horizontal wells and typewells with an engineering-style 4-chart dashboard:

- **Gamma Ray Log** — GR vs projected horizontal distance along the well azimuth
- **Well Path Projection** — Z (TVD) vs projected horizontal distance with formation surface overlays
- **TVT Correlation** — full-depth GR vs True Vertical Thickness with geology boundaries
- **TVT Last 200 ft** — zoomed view of the active drilling window

Additional features:
- Well and typewell selection from auto-scanned `data/` directory
- "Matched only" typewell filter that highlights the typewell sharing the same well ID
- Prediction start marker (first row where `TVT_input` is NaN) on the well path
- Azimuth computed automatically from first/last valid X/Y coordinates

## Project Structure

- `app.py`: Streamlit entrypoint and UI layout
- `src/config.py`: Paths, formation column names, and plotting constants
- `src/data_loader.py`: Well file discovery and CSV loading (pandas)
- `src/validators.py`: Schema validation for horizontal well and typewell DataFrames
- `src/calculations.py`: Azimuth, horizontal projection, prediction start, geology boundary extraction
- `src/plotting.py`: Plotly figure builders for all four dashboard charts
- `requirements.txt`: Runtime dependencies

## Run Locally

1. Install dependencies:

	```bash
	python -m pip install -r requirements.txt
	```

2. Start the app:

	```bash
	streamlit run app.py
	```

3. Open the URL printed in the terminal (defaults to `http://localhost:8501`).

## Data Expectations

Place well files in `data/` using this naming convention:

- `{WELLID}__horizontal_well.csv`
- `{WELLID}__typewell.csv`

Where `WELLID` is an 8-character lowercase hex hash (for example, `015fe0d2`).

### Horizontal well columns

`MD`, `X`, `Y`, `Z`, `GR`, `TVT_input`, and optionally formation columns (`ANCC`, `ASTNU`, `ASTNL`, `EGFDU`, `EGFDL`, `BUDA`).

### Typewell columns

`TVT`, `GR`, `Geology` (string formation label).
