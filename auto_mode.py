from daq import DAQ
import time

daq = DAQ()

daq.connect()

try:

    while True:

        record = daq.acquire_once()

        print(record)

        time.sleep(daq.period)

except KeyboardInterrupt:

    print("\nAcquisition stopped by user.")

finally:

    daq.disconnect()