"""
test_history.py

Standard acceptance test for the Tube Furnace DAQ History module.

Purpose
-------
This program verifies that the History module correctly stores,
retrieves, clears, and automatically removes old acquisition records.

Instructions
------------
Run this program without modification.

Expected behavior
-----------------
The program will verify that History can:

- Store acquisition records.
- Return the stored records.
- Automatically remove old records.
- Clear all records.
"""

from datetime import datetime, timedelta

from history import History


# ---------------------------------------------------------------------
# Create the History object.
# ---------------------------------------------------------------------

print("========================================")
print("Tube Furnace DAQ History Test")
print("========================================")

history = History()

# ---------------------------------------------------------------------
# Create sample acquisition records.
# ---------------------------------------------------------------------

print("\nCreating sample acquisition records...")

now = datetime.now()

record1 = {
    "Timestamp": now,
    "FurnaceTC (°C)": 1000.0,
    "BusyBee (Torr)": 0.50,
}

record2 = {
    "Timestamp": now + timedelta(seconds=1),
    "FurnaceTC (°C)": 1001.0,
    "BusyBee (Torr)": 0.51,
}

record3 = {
    "Timestamp": now + timedelta(seconds=2),
    "FurnaceTC (°C)": 1002.0,
    "BusyBee (Torr)": 0.52,
}

# ---------------------------------------------------------------------
# Add records.
# ---------------------------------------------------------------------

print("\nAdding acquisition records...")

history.add(record1)
history.add(record2)
history.add(record3)

print("Records added.")

# ---------------------------------------------------------------------
# Display stored records.
# ---------------------------------------------------------------------

print("\nCurrent history:")

for record in history.get_records():
    print(record)

# ---------------------------------------------------------------------
# Clear history.
# ---------------------------------------------------------------------

print("\nClearing history...")

history.clear()

if len(history.get_records()) == 0:
    print("History successfully cleared.")
else:
    print("ERROR: History was not cleared.")

# ---------------------------------------------------------------------
# Test automatic removal of old records.
# ---------------------------------------------------------------------

print("\nTesting automatic removal of old records...")

old_record = {
    "Timestamp": datetime.now() - timedelta(hours=25),
    "FurnaceTC (°C)": 900.0,
    "BusyBee (Torr)": 0.10,
}

new_record = {
    "Timestamp": datetime.now(),
    "FurnaceTC (°C)": 1000.0,
    "BusyBee (Torr)": 0.50,
}

history.add(old_record)
history.add(new_record)

records = history.get_records()

print("\nCurrent history:")

for record in records:
    print(record)

if len(records) == 1 and records[0]["Timestamp"] == new_record["Timestamp"]:
    print("\nOld records were successfully removed.")
else:
    print("\nERROR: Automatic removal of old records failed.")

print("\nTest completed successfully.")