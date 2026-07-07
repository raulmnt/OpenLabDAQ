"""
test_history.py

Basic test for the History class.
"""

from datetime import datetime, timedelta

from history import History
from measurement import Measurement


history = History()

print("Test 1: Empty history")
print(f"Measurements stored: {len(history.get_all())}")
print()


history.add(
    Measurement(
        name="FurnaceTC",
        value=900.0,
        unit="°C",
        timestamp=datetime.now() - timedelta(hours=25)
    )
)

print("Test 2: Added one old measurement")
print(f"Measurements stored: {len(history.get_all())}")
print()


history.add(
    Measurement(
        name="FurnaceTC",
        value=1000.0,
        unit="°C",
        timestamp=datetime.now()
    )
)

print("Test 3: Added a current measurement")
print(f"Measurements stored: {len(history.get_all())}")
print(f"Latest value: {history.get_latest().value}")
print()


history.clear()

print("Test 4: Clear history")
print(f"Measurements stored: {len(history.get_all())}")