#!/usr/bin/python3

# Verify that a hostname or IP address is accessible.

# Import needed modules.
import subprocess
import sys

# Set global variables.
MAX_WAIT = '3'

# Determine address to ping.
address = '127.0.0.1' # default
if len(sys.argv) > 1:
    address = sys.argv[1]

# Determine OS type and set shell_command accordingly.
if sys.platform == 'darwin':
    print("WARNING: This hasn't been tested on MacOS.")
if sys.platform == 'linux' or platform == 'linux2' or platform == 'darwin':
    shell_command = f"ping -w {MAX_WAIT} {address}"
elif sys.platform == 'win32':
    shell_command = f"ping -w {MAX_WAIT} {address}"
    # shell_command = f"ping /w {MAX_WAIT} {address}"
else:
    print(f"Platform \"{sys.platform}\" is not yet supported.")
    exit(1)

# Run shell command.
completed_process = subprocess.run(
    shell_command,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    shell=True,
)

# Set status depending on command returncode.
if completed_process.returncode == 0:
    status = 'up'
else:
    status = 'down'

# Print results.
print(f'Host "{address}" is {status}.')
