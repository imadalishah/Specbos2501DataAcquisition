import serial
import csv
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

def read_jeti_spectrum(port='COM8'):
    # Configure serial port
    ser = serial.Serial(
        port=port,
        baudrate=115200,  # spectraval 15x1 uses 921600; specbos uses 115200
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=10.0  # Generous timeout for hardware exposure limits
    )

    try:
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # 1. Trigger measurement
        # Parameters: 0=Auto Integration, 1=Measure Dark, 2=ASCII Output Format
        print("Triggering measurement (*meas:light 0 1 2)...")
        ser.write(b'*meas:light 0 1 2\r')

        # 2. Handshake Phase
        # Wait for ACK (\x06)
        ack = ser.read(1)
        if ack != b'\x06':
            raise ConnectionError(f"Device did not acknowledge. Received: {ack}")

        print("Measurement accepted. Waiting for hardware to complete exposure...")

        # Wait for BELL (\x07)
        while True:
            char = ser.read(1)
            if char == b'':
                raise TimeoutError("Timeout waiting for measurement to complete.")
            if char == b'\x07':
                print("Measurement complete. Receiving data...")
                break

        # 3. Data Fetch Phase
        # Format 2 streams data delimited by '\r' and closes with '\x03' (ETX).
        # We read the entire block at once until we hit the ETX byte.
        raw_bytes = ser.read_until(b'\x03')

        # 4. Parse the Data
        # Decode and strip out control characters like STX (\x02) and ETX (\x03)
        raw_text = raw_bytes.decode('utf-8', errors='ignore').replace('\x02', '').replace('\x03', '')

        # Split by Carriage Return to get individual lines
        raw_lines = raw_text.split('\r')

        wavelengths = []
        intensities = []

        for line in raw_lines:
            line = line.strip()
            if not line:
                continue

            # JETI Format 2 separates columns with a Tab (\t)
            parts = line.split('\t')
            if len(parts) >= 2:
                try:
                    w = float(parts[0])
                    val = float(parts[1])
                    wavelengths.append(w)
                    intensities.append(val)
                except ValueError:
                    pass  # Skip non-numeric header lines silently

        return wavelengths, intensities

    finally:
        ser.close()


def save_to_csv(wavelengths, intensities, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Wavelength (nm)', 'Intensity'])
        for w, i in zip(wavelengths, intensities):
            writer.writerow([w, i])
    print(f"Data saved to {filename}")


def plot_spectrum(wavelengths, intensities, filename='spectral_plot.png'):
    plt.figure(figsize=(24, 8))
    plt.plot(wavelengths, intensities, color='blue', linewidth=1)

    # Set x-ticks (Every 20 units)
    start, end = min(wavelengths), max(wavelengths)
    plt.xticks(np.arange(start, end + 1, 20))

    plt.title(f"Spectral Power Distribution - {datetime.now().strftime('%H:%M:%S')}")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity")
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.savefig(filename)
    print(f"Plot saved to {filename}")
    plt.close()


if __name__ == "__main__":
    w, i = read_jeti_spectrum('COM8')    # Check Connected COM Port
    if w and i:
        print(f"\nSuccess! Parsed {len(w)} spectral data points.")
        print(f"Sample data -> Wavelength: {w[0]} nm, Value: {i[0]}")
        # Create a timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        save_to_csv(w, i, f'measurement_{timestamp}.csv')
        plot_spectrum(w, i, f'spectrum_{timestamp}.png')
    else:
        print("\nMeasurement failed.")
