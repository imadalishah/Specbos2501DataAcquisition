# JETI Spectroradiometer Data Acquisition

Tools for communicating with a JETI spectroradiometer (tested on a **specbos 2501**) via a serial connection: triggering a measurement, parsing the resulting ASCII data, and saving results as CSV/plot output.

The repo provides two ways to use this:

* **`jeti_spectro.py`** — an importable Python API (`JetiSpectrometer` class) for use in your own scripts/pipelines.
* **`standalone_run.py`** — the original self-contained script; no import required, just run it directly.
* **`run.py`** — a CLI wrapper built on top of `jeti_spectro.py`, functionally equivalent to `standalone_run.py` but using the library internally.

```
repo/
├── standalone_run.py     # original self-contained script
├── run.py                # CLI wrapper using jeti_spectro.py
└── jeti_spectro.py        # importable API (JetiSpectrometer class)
```

## Prerequisites

* Python 3.x
* `pyserial`
* `matplotlib`
* `numpy`

```bash
pip install pyserial matplotlib numpy
```

## Usage

### Option A: Command line (standalone script or CLI wrapper)

1. **Identify your port:** check your OS Device Manager or terminal (e.g., `COM8` on Windows, `/dev/ttyUSB0` on Linux/macOS).
2. **Run it:**
   ```bash
   python standalone_run.py COM8
   ```
   or, equivalently, using the library-backed CLI:
   ```bash
   python run.py COM8
   ```
   *If no port is passed, both default to `COM8`.*

Either produces the same two output files (see below).

### Option B: As a library, in your own code

```python
from jeti_spectro import JetiSpectrometer, JetiError

with JetiSpectrometer(port="COM8") as jeti:
    wavelengths, intensities = jeti.measure()
    jeti.save_csv(wavelengths, intensities, "measurement.csv")
    jeti.plot(wavelengths, intensities, "spectrum.png")
```

`measure()` only returns the data — it does **not** write files on its own. Use `save_csv()` / `plot()` (or your own downstream analysis) as needed. Handshake failures, timeouts, and unparseable responses raise `JetiError`, so wrap calls in `try/except JetiError` for automated/unattended runs.

## Configuration Notes

* **Data format:** the library/scripts send `*meas:light 0 1 2` to trigger an auto-exposed light measurement. The trailing `2` requests **JETI Format 2** (tab-delimited ASCII rows). JETI instruments support other output formats (including binary); only Format 2 is implemented here. See your device's serial/remote command reference for the full list.
* **Protocol source:** command syntax and the handshake sequence (STX `\x02` / ACK `\x06` / BELL `\x07` / ETX `\x03`) follow JETI Technische Instrumente GmbH's serial command reference for the specbos/spectraval line. Consult your instrument's manual for the authoritative spec, as behavior may vary by firmware revision.
* **Device compatibility:** verified only on the **specbos 2501**. Other specbos models and the spectraval 15x1 are believed to share the same protocol family, but this has not been confirmed — check handshake behavior on your specific unit before relying on this for measurements.
* **Baud rate:** defaults to `115200` (typical for specbos). For a **spectraval 15x1**, pass `baudrate=921600` to `JetiSpectrometer(...)`, or edit the constant in `standalone_run.py` if using the standalone script.
* **Timeout limits:** a 10-second serial timeout is configured by default (`timeout` parameter). Increase it if your measurement environment is very dark and requires long exposure integrations.

## Output Files

When called via the CLI (`standalone_run.py` or `run.py`), two timestamped files are written to the working directory:

* `measurement_YYYYMMDD_HHMMSS.csv` — `Wavelength (nm)` vs `Intensity`.
* `spectrum_YYYYMMDD_HHMMSS.png` — an SPD line plot with 20 nm tick markers.

When used as a library, file output is opt-in via `save_csv()` / `plot()`.

**Units note:** `Intensity` reflects whatever the instrument returns for Format 2 output as configured — raw counts vs. calibrated irradiance depends on your device's calibration state. Confirm your instrument's calibration/output settings before treating these values as absolute radiometric quantities.

## License

The Python code in this repository is licensed under the [MIT License](LICENSE). This covers the code only — it grants no rights to JETI's proprietary command protocol or hardware, and a JETI instrument is required to use this tool at all.
