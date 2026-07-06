"""Responsibilities

Your driver must:

Connect to the instrument.
Disconnect from the instrument.
Request one measurement.
Report the communication status.
Return measurements as Measurement objects.

The driver must not:

Save CSV files.
Plot data.
Store history.
Create timestamps outside the Measurement object.

Each driver must implement:
connect()
disconnect()
read()
get_status()






PSEUDOCODE:


Class Instrument

    connect()

        Open communication port

        Verify communication

        Return True if successful

    disconnect()

        Close communication port

    read()

        Send instrument command

        Receive reply

        Convert reply into engineering units

        Create Measurement object

        Return Measurement

    get_status()

        Return communication status
"""