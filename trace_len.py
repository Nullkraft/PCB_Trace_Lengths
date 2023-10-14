"""
PCB Trace Length Measurement Tool

Purpose:
This script monitors a given .pcb file for changes and computes the
length of selected traces within the file. Traces are identified as
lines containing specific keywords, and their lengths are calculated
based on parsed coordinates.

Author(s):
Mark E. Stanley

Date Created:
26 Aug. 2023

Dependencies:
- re (built-in): Provides regular expression matching operations.
- sys (built-in): Access to Python interpreter variables.
- pyinotify: Used for monitoring file changes in real-time.
- time (built-in): Provides various time-related functions.

Usage:
Run from the command line with the path to the .pcb file as an argument:
    python [script_name].py path_to_pcb_file.pcb

Note: 'pip install pyinotify'

License:
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import re
import pyinotify
import time


class EventHandler(pyinotify.ProcessEvent):
  def __init__(self, filename):
    self.filename = filename
    self.saved_files = {}
    self.last_printout = None  # Add a variable to store the last printout

  def process_IN_MODIFY(self, event):
    '''
    The OS generates multiple FileSave events during file modifications.
    In the earliest events, the file might not have been fully saved,
    leading to incomplete data and inaccurate results.
    '''
    time.sleep(0.1)  # Delay ensures all data is written to the file
    self.process_file()

  def process_file(self):
    selected_lines = []
    with open(self.filename, 'r') as pcb:
      for line in pcb:
        if 'Line' in line and ('connected' in line or 'selected' in line):
          selected_lines.append(line)
    # Generate the output string
    output = []
    traces = []
    while selected_lines:
      trace = self.get_trace(selected_lines, selected_lines[0])
      traces.append(trace)
    for idx, trace in enumerate(traces):
      total_length = sum(self.line_length(*self.parse_coordinates(line)) for line in trace)
      output.append(f" Trace {idx + 1}:\t{total_length:.2f} mils")
    # Check against the last printout and only print if it's something new
    output_str = "\n".join(output)
    if output_str != self.last_printout:
      print(output_str)
      self.last_printout = output_str

  def parse_coordinates(self, line):
    # Extract all the numbers and units from the line
    coordinates = re.findall(r'(\d+\.?\d*)(mil|mm)', line)[:4]  # Only using the first 4 elements
    # Convert the coordinates to the standard unit (using mil as the standard unit in this case)
    values = []
    for value, unit in coordinates:
      value = float(value)
      if unit == 'mm':
        value = value * 39.37  # 1mm = 39.37mil
      values.append(value)
    x1, y1, x2, y2 = values
    return x1, y1, x2, y2

  def line_length(self, x1, y1, x2, y2):
    # Pythagorean theorem
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

  def find_connected_line(self, lines, x, y):
    for line in lines:
      x1, y1, x2, y2 = self.parse_coordinates(line)
      if (x1, y1) == (x, y) or (x2, y2) == (x, y):
        return line
    return None

  def get_trace(self, lines, start_line):
    trace = [start_line]
    lines.remove(start_line)
    # Use a set to ensure unique endpoints and a list to loop over the trace's endpoints
    endpoints = {self.parse_coordinates(start_line)[:2], self.parse_coordinates(start_line)[2:]}
    while endpoints:
      x, y = endpoints.pop()
      # Look for a line that connects to the current endpoint
      next_line = self.find_connected_line(lines, x, y)
      if next_line:
        trace.append(next_line)
        lines.remove(next_line)
        # Check the opposite end of the line to see if it's a new endpoint
        x1, y1, x2, y2 = self.parse_coordinates(next_line)
        if (x, y) == (x1, y1) and (x2, y2) not in endpoints:
          endpoints.add((x2, y2))
        elif (x, y) == (x2, y2) and (x1, y1) not in endpoints:
          endpoints.add((x1, y1))
    return trace


def measure_selected_lines(file_path):
  wm = pyinotify.WatchManager()
  handler = EventHandler(file_path)
  notifier = pyinotify.Notifier(wm, handler)
  wm.add_watch(file_path, pyinotify.IN_MODIFY)
  notifier.loop()


if __name__ == '__main__':
  import sys
  # Check if a file name is given as a command line argument
  if len(sys.argv) > 1:
    filename = sys.argv[1]
    path_to_watch = filename
    measure_selected_lines(path_to_watch)
  else:
    print("Error: Please provide a .pcb filename as an argument.")



























