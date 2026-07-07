"""
test_logger.py

Standard acceptance test for the Tube Furnace DAQ Logger.

Purpose
-------
This program verifies that the Logger correctly creates a CSV file,
writes the header, appends acquisition records, and closes the file.

Instructions
------------
Run this program without modification.

Expected behavior
-----------------
The program will verify that the Logger can:

- Create the logging directory.
- Create a new CSV file.
- Write the CSV header.
- Append acquisition records.
- Close the file.

After running this program, verify that a CSV file has been created
inside the Data directory and that it contains the expected data.
"""

from logger import Logger


# ---------------------------------------------------------------------
# Create a sample acquisition record.
# ---------------------------------------------------------------------

record = {
    "Timestamp": "2026-07-07 12:00:00",
    "FurnaceTC (°C)": 1000.25,
    "BusyBee (Torr)": 0.52,
    "Hornet (Torr)": 0.48,
}

# ---------------------------------------------------------------------
# Create the Logger.
# ---------------------------------------------------------------------

print("========================================")
print("Tube Furnace DAQ Logger Test")
print("========================================")

logger = Logger("Data")

# ---------------------------------------------------------------------
# Create a new log file.
# ---------------------------------------------------------------------

print("\nCreating new log file...")

logger.new_file(record)

print("Log file created.")

# ---------------------------------------------------------------------
# Write several acquisition records.
# ---------------------------------------------------------------------

print("\nWriting acquisition records...")

for i in range(5):

    record["Timestamp"] = f"2026-07-07 12:00:0{i}"
    record["FurnaceTC (°C)"] += 0.5

    logger.write(record)

print("Records written.")

# ---------------------------------------------------------------------
# Close the log file.
# ---------------------------------------------------------------------

print("\nClosing log file...")

logger.close()

print("Logger closed.")

print("\nTest completed successfully.")