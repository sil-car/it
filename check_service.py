#!/usr/bin/python3

# Import commands from modules
from subprocess import PIPE, run
from sys import platform

# Global variables
SERVICENAME = "wuauserv"
EXPECTED_COUNT = 1

# Determine OS type and set shell_command accordingly.
if platform == 'darwin':
    print("WARNING: This hasn't been tested on MacOS.")
if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
    shell_command = "pgrep " + SERVICENAME + " -c"
elif platform == 'win32':
    shell_command = "sc query " + SERVICENAME + " | find \"RUNNING\" /c"
else:
    print(f"Platform \"{platform}\" is not yet supported.")
    exit(1)

# Note: this does not throw error on non-zero exit code.
# The command will give us a numeric count of the number of running services/processe.
completed_process = run(shell_command,  check=False, stdout=PIPE, shell=True)
if completed_process.returncode == 0:
  command_output_as_str = completed_process.stdout.decode()
  command_output_no_returns = command_output_as_str.strip()
  number_of_procs = int(command_output_no_returns)
else:
  number_of_procs = 0

if number_of_procs != EXPECTED_COUNT:
  print(f'Unexpected number of processes found: {number_of_procs}')
else:
  print("Process found!")	