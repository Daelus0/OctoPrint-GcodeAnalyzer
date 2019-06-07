import re
import json
from collections import defaultdict

dd = lambda: defaultdict(dd)

TIME_UNITS_TO_SECONDS = defaultdict(
    lambda: 0,
    {
        "s": 1,
        "second": 1,
        "seconds": 1,
        "m": 60,
        "min": 60,
        "minute": 60,
        "minutes": 60,
        "h": 60*60,
        "hour": 60*60,
        "hours": 60*60,
        "d": 24*60*60,
        "day": 24*60*60,
        "days": 24*60*60,
    })

def process_time_text(time_text):
  """Given a string like "5 minutes, 4 seconds + 82 hours" return the total in seconds"""
  total = 0
  for time_part in re.finditer('([0-9.]+)\s*([a-zA-Z]+)', time_text):
    quantity = float(time_part.group(1))
    units = TIME_UNITS_TO_SECONDS[time_part.group(2)]
    total += quantity * units
  return total

def get_analysis_from_gcode(machinecode_path):
  """Extracts the analysis data structure from the gocde.
  
  The analysis structure should look like this:
  http://docs.octoprint.org/en/master/modules/filemanager.html#octoprint.filemanager.analysis.GcodeAnalysisQueue
  (There is a bug in the documentation, estimatedPrintTime should be in seconds.)
  Return None if there is no analysis information in the file.
  """
  filament_length = None
  filament_volume = None
  printing_seconds = None
  with open(machinecode_path) as gcode_lines:
    for gcode_line in gcode_lines:
      if not gcode_line[0].startswith(";"):
        continue # This saves a lot of time
      m = re.match('\s*;\s*filament used\s*=\s*([0-9.]+)\s*mm\s*\(([0-9.]+)cm3\)\s*', gcode_line)
      if m:
        filament_length = [float(m.group(1))]
        filament_volume = [float(m.group(2))]
      #PrusaSlicer 2.0.0 Formating for length in mm
      m = re.match('\s*;\s*filament used\s*\[mm\]\s*=\s*([, 0-9.]+)\s*', gcode_line)
      if m:
	    filament_length = [float(x) for x in m.group(1).split(", ")]
      #PrusaSlicer 2.0.0 Formating for volume in cm3
	  m = re.match('\s*;\s*filament used\s*\[cm3\]\s*=\s*([, 0-9.]+)\s*', gcode_line)
      if m:
        filament_length = [float(x) for x in m.group(1).split(", ")]
    
      #inclusive to PrusaSlicer 2.0.0 Formating only capturing "Normal Mode"
      m = re.match('\s*;\s*estimated printing time\s*(?:\(normal mode\)\s*)?=\s(.*)\s*', gcode_line)
      if m:
        printing_seconds = process_time_text(m.group(1))

  # Now build up the analysis struct
  analysis = None
  if printing_seconds is not None or filament_length is not None or filament_volume is not None:
    dd = lambda: defaultdict(dd)
    analysis = dd()
    if printing_seconds is not None:
      analysis['estimatedPrintTime'] = printing_seconds
    if filament_length is not None:
	  for x in len(filament_length)
	    analysis['filament']['tool' + str(x)]['length'] = filament_length
    if filament_volume is not None:
	  for x in len(filament_volume)
        analysis['filament']['tool' + str(x)]['volume'] = filament_volume
    return json.loads(json.dumps(analysis)) # We need to be strict about our return type, unfortunately.
  return None
