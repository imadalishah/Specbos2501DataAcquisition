# JETI Spectroradiometer Data Acquisition Script

This script communicate with JETI spectroradiometer (e.g., specbos series) via a serial connection. It triggers a measurement, parses the resulting ASCII data, saves the results to a CSV file, and generates a spectral plot.

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

1. **Configure your Port:** Check your device manager to identify the correct COM port (e.g., `COM8` on Windows, or `/dev/ttyUSB0` on Linux/macOS).
2. **Update Script:** Update the port string in the `if __name__ == "__main__":` block:
```python
w, i = read_jeti_spectrum('YOUR_PORT_HERE')

```


3. **Run the script:**
```bash
python your_script_name.py

```



## Configuration Notes

* **Baudrate:** The script defaults to `115200` (typical for specbos). If you are using a **spectraval 15x1**, change the `baudrate` parameter in `read_jeti_spectrum` to `921600` or check documentation of the respective product.
* **Timeout:** The script sets a 10-second timeout. If your measurement integration time is very long, you may need to increase the `timeout` parameter in the `serial.Serial` configuration.

## Output Files

The script will generate two files in the current working directory, prefixed with the current timestamp:

* `measurement_YYYYMMDD_HHMMSS.csv`: Contains tabular data (Wavelength, Intensity).
* `spectrum_YYYYMMDD_HHMMSS.png`: A visual plot of the spectral power distribution.
