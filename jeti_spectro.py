"""
jeti_spectro.py

A small importable API for acquiring spectra from JETI spectroradiometers
(tested: specbos 2501) over a serial connection.

Example
-------
>>> from jeti_spectro import JetiSpectrometer
>>> with JetiSpectrometer(port="COM8") as jeti:
...     wavelengths, intensities = jeti.measure()
...     jeti.save_csv(wavelengths, intensities, "measurement.csv")
...     jeti.plot(wavelengths, intensities, "spectrum.png")

Protocol notes
--------------
Command syntax and the STX/ACK/BELL/ETX handshake follow JETI Technische
Instrumente GmbH's serial command reference for the specbos/spectraval
line. Consult your instrument's manual for the authoritative spec, as
behavior may vary by firmware revision. Verified only on specbos 2501;
other models in the family are expected but not confirmed to behave
identically.
"""

from __future__ import annotations

import csv
from datetime import datetime
from typing import List, Tuple, Optional

import numpy as np
import serial


class JetiError(Exception):
    """Raised for handshake failures, timeouts, or malformed responses."""


class JetiSpectrometer:
    """
    API wrapper around a JETI spectroradiometer connected via serial.

    Parameters
    ----------
    port : str
        Serial port, e.g. "COM8" or "/dev/ttyUSB0".
    baudrate : int
        115200 is typical for specbos. Use 921600 for spectraval 15x1.
    timeout : float
        Serial read timeout in seconds. Increase for long dark-environment
        exposures.
    auto_open : bool
        If True (default), the port is opened immediately on construction.
        Set False if you want to call .open() yourself.
    """

    def __init__(
        self,
        port: str = "COM8",
        baudrate: int = 115200,
        timeout: float = 10.0,
        auto_open: bool = True,
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._ser: Optional[serial.Serial] = None
        if auto_open:
            self.open()

    # -- connection management -------------------------------------------------

    def open(self) -> None:
        """Open the serial connection."""
        if self._ser and self._ser.is_open:
            return
        self._ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )

    def close(self) -> None:
        """Close the serial connection."""
        if self._ser and self._ser.is_open:
            self._ser.close()

    def __enter__(self) -> "JetiSpectrometer":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    @property
    def is_open(self) -> bool:
        return bool(self._ser and self._ser.is_open)

    # -- measurement -------------------------------------------------------------

    def measure(self, fmt: int = 2) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trigger a measurement and return the parsed spectrum.

        Parameters
        ----------
        fmt : int
            JETI output format. Only format 2 (tab-delimited ASCII) is
            currently supported/parsed by this API.

        Returns
        -------
        (wavelengths, intensities) as numpy arrays.

        Raises
        ------
        JetiError
            If the device does not acknowledge, times out, or format is
            unsupported.
        """
        if fmt != 2:
            raise NotImplementedError(
                "Only JETI Format 2 (tab-delimited ASCII) is currently supported."
            )
        if not self.is_open:
            self.open()

        ser = self._ser
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        ser.write(f"*meas:light 0 1 {fmt}\r".encode())

        ack = ser.read(1)
        if ack != b"\x06":
            raise JetiError(f"Device did not acknowledge measurement. Received: {ack!r}")

        while True:
            char = ser.read(1)
            if char == b"":
                raise JetiError("Timeout waiting for measurement to complete.")
            if char == b"\x07":
                break

        raw_bytes = ser.read_until(b"\x03")
        raw_text = (
            raw_bytes.decode("utf-8", errors="ignore")
            .replace("\x02", "")
            .replace("\x03", "")
        )

        wavelengths: List[float] = []
        intensities: List[float] = []
        for line in raw_text.split("\r"):
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                try:
                    wavelengths.append(float(parts[0]))
                    intensities.append(float(parts[1]))
                except ValueError:
                    pass  # skip non-numeric header lines

        if not wavelengths:
            raise JetiError("No valid spectral data parsed from device response.")

        return np.array(wavelengths), np.array(intensities)

    # -- output helpers ------------------------------------------------------------

    @staticmethod
    def save_csv(wavelengths, intensities, filename: str) -> str:
        """Write (wavelength, intensity) pairs to a CSV file. Returns the filename."""
        with open(filename, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Wavelength (nm)", "Intensity"])
            for w, i in zip(wavelengths, intensities):
                writer.writerow([w, i])
        return filename

    @staticmethod
    def plot(wavelengths, intensities, filename: str = "spectrum.png") -> str:
        """Save a spectral plot (PNG). Returns the filename."""
        import matplotlib.pyplot as plt  # local import: keeps plotting optional

        plt.figure(figsize=(24, 8))
        plt.plot(wavelengths, intensities, color="blue", linewidth=1)
        start, end = min(wavelengths), max(wavelengths)
        plt.xticks(np.arange(start, end + 1, 20))
        plt.title(f"Spectral Power Distribution - {datetime.now().strftime('%H:%M:%S')}")
        plt.xlabel("Wavelength (nm)")
        plt.ylabel("Intensity")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.savefig(filename)
        plt.close()
        return filename
