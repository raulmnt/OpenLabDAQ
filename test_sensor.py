"""
test_sensor.py

Standard acceptance test for Tube Furnace DAQ sensor drivers.

Purpose
-------
This program verifies that a sensor driver correctly implements the
Tube Furnace DAQ communication standard.

Instructions
------------
1. Import the sensor class to be tested.
2. Assign the sensor class to SENSOR.
3. Set the correct communication PORT.
4. Run this program.

If the driver follows the DAQ communication standard, no other
modifications to this file should be necessary.

Expected behavior
-----------------
The program will verify that the driver can:

- Connect to the instrument.
- Report the correct sensor name.
- Report the correct engineering unit.
- Return a measurement as a float.
- Disconnect correctly.
- Reject read requests after disconnecting.
"""

import sys

# ---------------------------------------------------------------------
# Select the sensor driver to test.
# Change ONLY these two lines.
# ---------------------------------------------------------------------

from sensors.LightSensor import LightSensor

SENSOR = LightSensor
PORT = "COM7"

# ---------------------------------------------------------------------
# Standard DAQ communication test.
# Do not modify the code below.
# ---------------------------------------------------------------------

print("========================================")
print("Tube Furnace DAQ Sensor Driver Test")
print("========================================")

# Create the sensor object.
sensor = SENSOR(PORT)

# ---------------------------------------------------------------------
# Test connection
# ---------------------------------------------------------------------

print("\nConnecting...")

try:
    sensor.connect()
    print("Connection successful.")
except Exception as error:
    print(f"Connection failed: {error}")
    sys.exit()

# ---------------------------------------------------------------------
# Test sensor information
# ---------------------------------------------------------------------

print("\nSensor Information")

print(f"Name : {sensor.NAME}")
print(f"Unit : {sensor.UNIT}")

# ---------------------------------------------------------------------
# Test measurement
# ---------------------------------------------------------------------

print("\nReading measurement...")

value = sensor.read()

if not isinstance(value, float):
    print("ERROR: read() did not return a float.")
    sys.exit()

print(f"Value: {value}")

# ---------------------------------------------------------------------
# Test disconnect
# ---------------------------------------------------------------------

print("\nDisconnecting...")

sensor.disconnect()

print("Disconnected.")

# ---------------------------------------------------------------------
# Verify that reading after disconnect raises an exception.
# ---------------------------------------------------------------------

print("\nAttempting to read after disconnect...")

try:
    sensor.read()
    print("ERROR: Driver allowed reading after disconnect.")
except Exception as error:
    print(f"Expected exception: {error}")

print("\nTest completed successfully.")

'''
If the driver follows the Tube Furnace DAQ communication standard, the output should look similar to this:

========================================
Tube Furnace DAQ Sensor Driver Test
========================================

Connecting...
Connection successful.

Sensor Information
Name : FurnaceTC 
Unit : °C 

Reading measurement...
Value: 998.7

Disconnecting...
Disconnected.

Attempting to read after disconnect...
Expected exception: FurnaceTC is not connected.

Test completed successfully.'''