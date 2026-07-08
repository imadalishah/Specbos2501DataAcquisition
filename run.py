import sys
from datetime import datetime
from jeti_spectro import JetiSpectrometer, JetiError


def main() -> int:
    target_port = sys.argv[1] if len(sys.argv) > 1 else "COM8"
    print(f"Connecting to JETI instrument on port: {target_port}")

    try:
        with JetiSpectrometer(port=target_port) as jeti:
            print("Triggering measurement (*meas:light 0 1 2)...")
            wavelengths, intensities = jeti.measure()
    except JetiError as e:
        print(f"\nMeasurement failed: {e}")
        return 1

    print(f"\nSuccess! Parsed {len(wavelengths)} spectral data points.")
    print(f"Sample data -> Wavelength: {wavelengths[0]} nm, Value: {intensities[0]}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = JetiSpectrometer.save_csv(wavelengths, intensities, f"measurement_{timestamp}.csv")
    png_path = JetiSpectrometer.plot(wavelengths, intensities, f"spectrum_{timestamp}.png")
    print(f"Data saved to {csv_path}")
    print(f"Plot saved to {png_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
