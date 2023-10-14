# PCB_Trace_Lengths
Python program that reports the length of a gEDA PCB trace marked with 'selected' or 'connected'.
The code monitors modifications to a `.pcb` file, which commonly represents printed circuit board designs. It identifies specific lines within the file containing certain keywords, then calculates and prints the total length of traces represented by these lines upon detecting changes.

## Libraries Used:
- **re**: Used for regular expression operations.
- **pyinotify**: Monitors file and directory changes in real-time on Linux.
- **time**: Introduces delays.

## Class `EventHandler`
This class inherits from `pyinotify.ProcessEvent` and handles events related to file modifications.

- `__init__(self, filename)`: Initializes instance with filename to watch, an empty dictionary for saved files, and a variable to store the last printout.
- `process_IN_MODIFY(self, event)`: Called when file is modified. Introduces a small delay ensuring all data is written before processing.
- `process_file(self)`: Processes the `.pcb` file, extracts and calculates trace lengths, then prints results if different from last printout.
- `parse_coordinates(self, line)`: Extracts coordinates from a line and converts to standard unit (mils).
- `line_length(self, x1, y1, x2, y2)`: Calculates line segment length using Pythagorean theorem.
- `find_connected_line(self, lines, x, y)`: Searches for a line connecting to point `(x, y)`.
- `get_trace(self, lines, start_line)`: Constructs a trace from lines starting with a given line.

## Function `measure_selected_lines`
Sets up inotify watch to monitor file modifications.

- Creates a `WatchManager` for managing file/directory watches.
- Instantiates `EventHandler` with file to watch.
- Uses `Notifier` for event loop and dispatching to handler.
- Adds file to watch list with `IN_MODIFY` flag (notifying only on modifications).
- Starts notifier's loop, awaiting events.

## Main Block
Checks for filename as command-line argument. If provided, calls `measure_selected_lines` with filename. Otherwise, prints error message.

## Summary
Script monitors a `.pcb` file for changes. On modification, it checks lines for traces, computes their lengths, and prints results if different from previous output.


## Example
  ```python3 trace_len.py <path_to_pcb_file.pcb>```

When the program starts it will just be waiting for you to save the file. If you have selected or
highlighted any lines it will calculate and display the length of those lines. In PCB you can high-
light an entire trace by hovering over the trace and pressing the 'f' key. Now when you save the
program will report the length of the entire trace. If, instead, you use the mouse to click on one
line at a time you can press shift-click to select multiple traces. If the selections are connected
to each other then the program will report the combined, or total length. If they are not connected
then you will get a report for each trace that you selected.

To exit the program press Ctrl-C

![Screen capture showing that none of the traces have been selected](./images/pwrsupvwi_no_select.png)

