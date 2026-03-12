
# Crazyflie Localization & Environment Visualization 🛰️

This module is focused on **processing and visualizing Indoor Positioning System (IPS) data**, particularly using the **Lighthouse positioning system**.  
It converts raw logs into structured data and provides **interactive 3D visualizations** to identify blind spots, sensor weaknesses, and flight environment characteristics.

---

## Key Features

- Convert raw telemetry logs into structured pandas DataFrames.
- Sync position and Lighthouse status data to account for timestamp offsets (<15ms).
- Filter invalid or outlier coordinates.
- Generate JSON files for visualization (e.g., `light_status.json`, `light_bsActive.json`, `light_bsCalCon.json`).
- Interactive 3D plots of IPS coverage and health.

---

## Files

### `dataframes_processing.py`
- Processes recorded telemetry logs and lighthouse data.
- Maps base station status, calibration, and tracking quality onto 3D coordinates.
- Generates JSON outputs ready for visualization.

### `visualize_flight_environment.py`
- Visualizes processed localization data in **interactive 3D plots**.
- Allows toggling between different visualization modes:
  - **bsAvailable**: Areas with the most base station coverage.
  - **status**: Overall tracking health.
  - **bsCalCon**: Zones where calibration data is successfully received.

---

## Workflow

1. **Data Logging (from `logging` module)**
   - Run `connect_log_param.py` to generate log files:
     - `log_variables.csv` — master log.
     - `statestimation_json.json` — high-frequency positions.
     - `lighthouse_json.json` — base station tracking status.

2. **Processing**
   - Align timestamps between position and lighthouse packets.
   - Filter invalid coordinates and synchronize logs.
   - Generate JSONs for visualization.

3. **Visualization**
   - Run `visualize_flight_environment.py`.
   - Explore coverage, calibration, and tracking quality interactively.
   - Identify blind spots and areas for IPS improvement.

---

## Requirements

- Python packages: `cflib`, `pandas`, `plotly`, `json`
- Input logs from `logging/connect_log_param.py` or equivalent flights.

---

## Purpose

The `localization` module allows researchers to:

- Analyze IPS performance and coverage.
- Visualize the 3D flight environment.
- Inspect sensor reliability and lighthouse beacon distribution.
- Support trajectory analysis, automated flight testing, and IPS system improvements.