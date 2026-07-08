# JETI Spectroradiometer Data Acquisition Script

This script communicate with JETI spectroradiometer (e.g., specbos 2501: In our demo) via a serial connection. It triggers a measurement, parses the resulting ASCII data, saves the results to a CSV file, and generates a spectral plot.

## Prerequisites

Ensure you have the following installed:

* Python 3.x
* `pyserial`
* `matplotlib`
* `numpy`

You can install the required libraries using pip:

```bash
pip install pyserial matplotlib numpy

```

## Usage

1. **Identify your Port:** Check your OS Device Manager or terminal to identify your instrument's port (e.g., `COM8` on Windows, or `/dev/ttyUSB0` on Linux/macOS).
2. **Run the script:** Pass your port directly as a command-line argument:
   ```bash
   python run.py COM8
   ```
   *If no argument is passed, the script defaults to `COM8`.*


3. **Run the script:**
```bash
python run.py COM8

```



## Configuration Notes

* **Data Format:** The script sends `*meas:light 0 1 2` to trigger an auto-exposed light measurement. The trailing `2` explicitly requests **JETI Format 2** (Tab-delimited ASCII data text rows).
* **Baudrate:** The script defaults to `115200` (typical for specbos). If you are using a **spectraval 15x1**, update the `baudrate` parameter inside `read_jeti_spectrum()` to `921600`.
* **Timeout Limits:** A 10-second serial timeout is configured. If your physical target environment is very dark and requires extra long exposure integrations, increase the `timeout` parameter in the `serial.Serial` definition block.

## Output Files

Upon a successful handshake and data stream reading, two timestamped files are written to your local working directory:

* `measurement_YYYYMMDD_HHMMSS.csv`: Tabular plain-text data mapping `Wavelength (nm)` against `Intensity`.
* `spectrum_YYYYMMDD_HHMMSS.png`: A high-resolution spectral power distribution (SPD) line plot with 20nm incremental markers.

## License

This project is licensed under the [MIT License](LICENSE) - feel free to use, modify, and distribute it.
