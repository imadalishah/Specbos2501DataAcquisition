# JETI Spectroradiometer Data Acquisition Script

This script communicates with a JETI spectroradiometer (tested on a **specbos 2501**) via a serial connection. It triggers a measurement, parses the resulting ASCII data, saves the results to a CSV file, and generates a spectral plot.

## Prerequisites

Ensure you have the following installed:

* Python 3.x
* `pyserial`
* `matplotlib`
* `numpy`

```bash
pip install pyserial matplotlib numpy
```

## Usage

1. **Identify your port:** Check your OS Device Manager or terminal to identify your instrument's port (e.g., `COM8` on Windows, or `/dev/ttyUSB0` on Linux/macOS).
2. **Run the script**, passing your port as a command-line argument:
```bash
   python standalone_run.py COM8
```
   *If no argument is passed, the script defaults to `COM8`.*

## Configuration Notes

* **Data format:** The script sends `*meas:light 0 1 2` to trigger an auto-exposed light measurement. The trailing `2` requests **JETI Format 2** (tab-delimited ASCII rows). JETI instruments support other output formats (including binary); this script only implements Format 2. See your device's serial/remote command reference for the full list.
* **Protocol source:** The command syntax and the handshake sequence (STX `\x02` / ACK `\x06` / BELL `\x07` / ETX `\x03`) follow JETI Technische Instrumente GmbH's serial command reference for the specbos/spectraval line. Consult your instrument's manual for the authoritative spec, as behavior may vary by firmware revision.
* **Device compatibility:** Verified only on the **specbos 2501**. Other specbos models and the spectraval 15x1 are believed to share the same protocol family, but this has not been confirmed — check handshake behavior on your specific unit before relying on this for measurements. If using a **spectraval 15x1**, update `baudrate` inside `read_jeti_spectrum()` to `921600` (default here is `115200`, typical for specbos).
* **Timeout limits:** A 10-second serial timeout is configured. If your measurement environment is very dark and requires long exposure integrations, increase the `timeout` parameter in the `serial.Serial` definition.

## Output Files

Upon a successful handshake and data read, two timestamped files are written to your working directory:

* `measurement_YYYYMMDD_HHMMSS.csv` — `Wavelength (nm)` vs `Intensity`.
* `spectrum_YYYYMMDD_HHMMSS.png` — an SPD line plot with 20 nm tick markers.

**Units note:** `Intensity` reflects whatever the instrument returns for Format 2 output as configured (e.g. raw counts vs. calibrated irradiance depends on your device's calibration state). Confirm your instrument's calibration/output settings before treating these values as absolute radiometric quantities.

## License

The Python script in this repository is licensed under the [MIT License](LICENSE). This covers the code only, i.e, it grants no rights to JETI's proprietary command protocol or hardware, and a JETI instrument is required to use this tool at all.
