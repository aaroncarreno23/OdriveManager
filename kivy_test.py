import math
import struct
import sys
import time
import os

from IPython.core.crashhandler import crash_handler_lite
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.uix import widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config, key
from kivy.core.window import Window
from pidev.kivy.DPEAButton import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
#import RPi.GPIO as GPIO
from pidev.kivy.ImageButton import ImageButton
import numpy as np
import random
import signal
from typing import Union, Tuple

import traceback

import odrive_helpers_2
from odrive_helpers_2 import *
from odrive_helpers_2 import digital_read
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen
odrv0 = str("207935A1524B")
odrive_board0 = find_odrive(odrv0)
assert odrive_board0.config.enable_brake_resistor is True, "Check for faulty brake resistor"
odrive_motor1 = ODriveAxis(odrive_board0.axis1)

Builder.load_file('main.kv')
print("main.kv loaded.")

Window.clearcolor = (0.4, 0.5, 0.2, 1) #white

sm = ScreenManager()



class MyApp(App):

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     Clock.schedule_once(lambda dt: self.initalize_thangs(), 1)
    #
    #
    # def initalize_thangs(self):
    #     self.odrive_board0 = None
    #     self.odrive_motor1 = None
    #     self.initialize_odrives()
    #     # self.reboot()
    #     # self.initialize_odrives()
    #     if self.odrive_board0 and self.odrive_motor1:
    #         # self.configure_calibrate_home_odrives()
    #         self.calibrate_odrive()
    #     else:
    #         print("ODrive initialization failed. Skipping configuration and homing")

    def build(self):
        self.title = "kivy test"
        return sm

    # def initialize_odrives(self):
    #     try:
    #         odrv0 = str("207935A1524B")
    #         self.odrive_board0 = find_odrive(odrv0)
    #         assert self.odrive_board0.config.enable_brake_resistor is True, "Check faulty brake resistor."
    #         self.odrive_motor1 = ODriveAxis(self.odrive_board0.axis1)
    #         print("Odrive initialized successfully")
    #     except Exception as e:
    #         print(f"Error initalizing ODrive(s): {e}")
    #
    # # def reboot(self):
    # #     try:
    # #         odrive_helpers_2.reboot_odrive(self.odrive_board0)
    # #         print("ODriveBoard0.")
    # #
    # #     except Exception as e:
    # #         print(f"Error reboot ODrive(s): {e}")
    # #
    # # def configure_calibrate_home_odrives(self):
    # #     try:
    # #         self.odrive_motor1.set_vel_gain(0.05)
    # #         self.odrive_motor1.axis.controller.config.pos_gain = 20
    # #         self.odrive_motor1.axis.motor.config.torque_lim = 10
    # #         self.odrive_motor1.set_calibration_current(10)
    # #         self.odrive_motor1.set_vel_limit(4)
    #           self.odrive_motor1.axis.motor.config.torque_lim = 20
    # #         print("ODrive configuration completed.")
    # #
    # #         if not self.odrive_motor1.is_calibrated():
    # #             print("calibrating OdriveMotor0...")
    # #             self.odrive_motor1.calibrate()
    # #         self.odrive_motor1.wait_for_motor_to_stop()
    # #         print("ODriveMotor0 calibration completed.")
    # #
    # #         print("Homing ODriveMotor0...")
    # #         self.odrive_motor1.home_with_endstop(-5,0,2)
    # #         self.odrive_motor1.wait_for_motor_to_stop()
    # #         self.odrive_board0.set_home()
    # #         self.odrive_motor1.set_pos(-0.5)
    # #         print("ODrive homing completed.")
    # #
    # #     except Exception as e:
    # #         print(f"Error setting ODrive(s): {e}")
    #
    # def calibrate_odrive(self):
    #     try:
    #         if not self.odrive_motor1.is_calibrated():
    #             print("calibrating OdriveMotor1")
    #             self.odrive_motor1.calibrate()
    #         self.odrive_motor1.wait_for_motor_to_stop()
    #         print("OdriveMotor1 calibratoin completed.")
    #     except Exception as e:
    #         print(f"Error setting ODrive(s): {e}")



class MainScreen(Screen):

    # if not odrive_motor1.is_calibrated():
    #         print("calibrating OdriveMotor1")
    #         odrive_motor1.calibrate()
    # odrive_motor1.wait_for_motor_to_stop()
    # print("OdriveMotor1 calibratoin completed.")

    def test(self):
        print("TEST")

    def quit_main(self):
        try:
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            App.get_running_app().stop()

    def home(self):
        print("Homing ODriveMotor1...")
        # self.odrive_motor1.home_with_endstop(-5, 0, 2)
        # self.odrive_motor1.wait_for_motor_to_stop()
        # self.odrive_board1.set_home()
        # self.odrive_motor1.set_pos(-0.5)
        print("ODrive homing completed.")

    def set_torque_value(self, slider, value):
        torque_value = value
        self.ids.torque_lim_label.text = f"Torque Limit: {value}"
        #self.odrive_motor1.axis.motor.config.torque_lim = torque_value
        print(f"Torque Limit: {value}")

    def set_pos(self, slider, value):
        pos_value = value
        self.ids.pos_label.text = f"Pos: {value: .1f}"
        #self.odrive_motor1.set_pos(pos_value)
        print(f"Pos: {value: .1f}")


sm.add_widget(MainScreen(name = 'kivy_test'))

try:
    MyApp().run()
except Exception as e:
    print(e)
    raise e

""""
ISSUE FOR:
[DEBUG  ] [Using selector] EpollSelector
- was not running project through pi but jsut through computer
- make sure running python3 through pi or pycharm(if pycharm is set up correctly)


The [DEBUG ] [Using selector] EpollSelector message is just Kivy 
telling you it’s using the default event loop on Linux. That’s harmless.

I have not seen this before and odrive with kivy has not bothered me. 
I have coded a repicla but it does not seem to work. 
Try to copy the exact code and see if it works. 

All AI is telling me is to use threads or changing event loop for kivy
but that does not seem right. 

MOVE POS IN TERMINAL - 

---IDEALLY YOU ADD odrv0.axis1.encoder.pos_estimate TO THE POS IS BUT IT 
---IS SMALL VALUE SO NOT NECESSARY
---KEEP IN MIND THIS IS ABSOLUTE POSITION

odrv0.axis1.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE

odrv0.axis1.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL

odrv0.axis1.controller.config.control_mode = ControlMode.POSITION_CONTROL

odrv0.axis1.controller.input_pos = 1

ODrive control utility v0.5.4

ODrive control utility v0.6.10.post0

"""