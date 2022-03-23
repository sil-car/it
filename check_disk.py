#!/usr/bin/python3

# Developed by Brian Yee and Nate Marti.

# Import needed commands from modules.
from subprocess import check_output
from sys import platform

# Set global variable.
THRESHOLD = 0.85

# Determine OS type and set shell_command accordingly.
if platform == 'darwin':
    print("WARNING: This hasn't been tested on MacOS.")
if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
    shell_command = "lsblk --bytes --output=FSAVAIL,MOUNTPOINT,SIZE | grep \"\s/\s\""
elif platform == 'win32':
    shell_command = "wmic logicaldisk GET Name,Size,FreeSpace | find /i \"C:\""
else:
    print(f"Platform \"{platform}\" is not yet supported.")
    exit(1)

# Run shell command and parse output.
command_output_as_bytes = check_output(shell_command, shell=True)
command_output_as_str = command_output_as_bytes.decode()
command_output_no_returns = command_output_as_str.strip()
parsed_output = command_output_no_returns.split()

# Define variables for usage numbers.
free_space = int(parsed_output[0]) # convert to a number
drive_letter = parsed_output[1]
drive_capacity = int(parsed_output[2]) # convert to a number

# Calculate usage numbers.
percentage_used = (drive_capacity - free_space) / drive_capacity
percentage_output = "{:.2%}".format(percentage_used)

# Output results.
print(f'Drive {drive_letter} has capacity {drive_capacity} and has free {free_space}')
print(f'This is {percentage_output}')

if (percentage_used > THRESHOLD):
    print('Drive is approaching capacity')
else:
    print('Drive is OK')
