#!/usr/bin/python3

# Developed by Brian Yee and Nate Marti.

# Import needed commands from modules.
import sys
import time
from pathlib import Path
from datetime import datetime,timezone,timedelta

# Set global variable.
OFFSET = 4 * 24 * 60 * 60 # 1 day

example_date = datetime.fromtimestamp(time.time() - OFFSET, timezone(timedelta(hours=1)))

found = 0
# Path will adapt the path to be platform specific.
# This is a sample file that looks like an apache log file.
path_to_file = Path("./datafiles/log_file")

if path_to_file.exists():
    with path_to_file.open("r", encoding="UTF-8") as log_file:
        lines = log_file.readlines()
        for line in lines:
            raw_line = line.strip()

            substring_start = raw_line.find('[')
            substring_end = raw_line.find(']')
            log_date = datetime.strptime(raw_line[(substring_start+1):(substring_end)], "%d/%b/%Y:%H:%M:%S %z")

            if log_date > example_date:
                found = 1
else:
    print("Error: opening file" + str(path_to_file), file=sys.stderr)
    exit(1)


if found:
    print(f"Log file entry found since {example_date}")
else:
    print(f"No recent log file entry found since {example_date}")
