"""
test_furnace_tc.py

Tests the FurnaceTC sensor driver.

This script verifies that the driver can:

- Connect to the configured instrument.
- Read the instrument status.
- Read a temperature measurement.
- Disconnect cleanly.
"""
print("Program started")

from config import load_config
from sensors.furnace_tc import FurnaceTC


# Load the user configuration.
config = load_config()

# Create the sensor object.
sensor = FurnaceTC(config["ports"]["FurnaceTC"])

print("========================================")
print("Testing FurnaceTC Driver")
print("========================================")

# ----------------------------------------------------------
# Test connection
# ----------------------------------------------------------

print("\nConnecting...")

connected = sensor.connect()

print(f"Connected: {connected}")

if not connected:
    print("Test aborted.")
    exit()

# ----------------------------------------------------------
# Test status
# ----------------------------------------------------------

print("\nReading status...")

status = sensor.get_status()

print(f"Status: {status}")

# ----------------------------------------------------------
# Test measurement
# ----------------------------------------------------------

print("\nReading measurement...")

measurement = sensor.read()

print(measurement)

# ----------------------------------------------------------
# Test disconnect
# ----------------------------------------------------------

print("\nDisconnecting...")

sensor.disconnect()

print("Disconnected.")


# ----------------------------------------------------------
# Test reding after disconnect
# ----------------------------------------------------------

print("\nTrying to read after disconnect...")

try:
    sensor.read()
except Exception as error:
    print("Expected error:", error)

print("\nAll tests completed.")