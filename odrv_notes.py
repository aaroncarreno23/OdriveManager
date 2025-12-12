
"""
Odrives use specific code to function. As you may know, we use the odrive helpers
library to use custom functions that are easier to use and read. It is important
to understand where the "raw" code comes from so you can adjust with the "raw" code
as needed. It also helps you learn the structure of the code.
You will mostly use "raw" odrive code when you use odrivetool. To access
that you have to ssh into your pi, then type in odrivetool. Here are three useful
"raw" codes that may be helpful while working with odrives.

1. <odrv>.<axis>.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
- to calibrate, make sure your odrive is in the middle of your axis for safety

2.<odrv>.<axis>.requested_state = AXIS_STATE_IDLE
- if you find your odrive becomes stuck, try this to get it unstuck

3.dump_errors(<odrv>) and <odrv>.clear_errors()
- if you find yourself having more issues try dumping the errors to find
- what the cause is. After fixing it, reset with the clear function

-------------------------------------------------------------------------------------------

Odrives work with three main parts

To check your firmware and hardware compatability, simply ssh into your pi and
then type odrivetool.

Make sure odrive hardware and firmware(version) is compatible. For example,
version v0.6.10 is not compatible with v3.6 but v3.6 is compatible with v0.5.4.
Make sure your hardware and firmware are compatible so your odrives can work properly.

-------------------------------------------------------------------------------------------

Check your limit switch.

<odrv>.config.gpio<x>_mode = GPIO_MODE_DIGITAL_PULL_UP
<odrv>.config.gpio<x>_mode = GPIO_MODE_DIGITAL_PULL_DOWN

and

<odrv>.<axis>.min_endstop.config.is_active_high = True/False



"""