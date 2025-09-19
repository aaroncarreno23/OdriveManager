import math
import struct
import sys
import time
import os

from IPython.core.crashhandler import crash_handler_lite
from PiKivyProjects.NewProject.main import AdminScreen
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
import RPi.GPIO as GPIO
from pidev.kivy.ImageButton import ImageButton
import numpy as np
import random
import signal
from typing import Union, Tuple

import traceback

import dpea_odrive.odrive_helpers
from dpea_odrive.odrive_helpers import *
from dpea_odrive.odrive_helpers import digital_read
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen

Builder.load_file('main.kv')
print("main.kv loaded.")

Window.clearcolor = (0.4, 0.5, 0.2, 1) #white

class MyApp(App):

    def __inti__(self, odrive_manager, **kwargs):
        super(MyApp, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def builf(self):
        self.title = "class ODriveManager"
        return sm

class ODriveManager:
    def __init__(self):
        self.odrive_board0 = None
        self.odrive_motor0 = None
        self.initialize_odrives()
        self.reboot()
        self.initialize_odrives()
        if self.odrive_board0 and self.odrive_motor0:
            self.configure_calibrate_home_odrives()
        else:
            print("ODrive initialization failed. Skipping configuration and homing")

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        print(f"Caught signal {signum}, initiating shutdown...")
        self.safe_shutdown()
        sys.exit(1)

    def safe_shutdown(self):
        print("Shutting down ODriveManager")

    def initialize_odrives(self):
        try:
            odrv0 = str("207935A1524B")
            self.odrive_board0 = find_odrive(odrv0)
            assert self.odrive_board0.config.enable_brake_resistor is True, "Check faulty brake resistor."
            self.odrive_motor0 = ODriveAxis(self.odrive_board0.axis0)
            print("Odrive initialized successfully")
            print("Digital inputs:")
            print(digital_read(self.odrive_motor0, 2))
        except Exception as e:
            print(f"Error initalizing ODrive(s): {e}")

    def configure_calibrate_home_odrives(self):
        try:
            self.odrive_motor0.set_vel_gain(0.05)
            self.odrive_motor0.axis.controller.config.pos_gain = 20
            self.odrive_motor0.axis.motor.config.torque_lim = 10
            self.odrive_motor0.set_calibration_current(10)
            self.odrive_motor0.set_vel_limit(4)
            print("ODrive configuration completed.")

            if not self.odrive_motor0.is_calibrated():
                print("calibrating OdriveMotor0...")
                self.odrive_motor0.calibrate()
            self.odrive_motor0.wait_for_motor_to_stop()
            print("ODriveMotor0 calibration completed.")

            print("Homing ODriveMotor0...")
            self.odrive_motor0.home_with_endstop(-5,0,2)
            self.odrive_motor0.wait_for_motor_to_stop()
            self.odrive_board0.set_home()
            self.odrive_motor0.set_pos(-0.5)
            print("ODrive homing completed.")

        except Exception as e:
            print(f"Error setting ODrive(s): {e}")

    def initialize_and_cch(self):
        try:
            self.initialize_odrives()
            print("ODrive(s) reconnected.")
            self.configure_calibrate_home_odrives()
            print("ODrive(s) ready for use.")
        except Exception as e:
            print(f"Error reconnecting ODrive(s): {e}")

    def reboot(self):
        try:
            dpea_odrive.odrive_helpers.reboot_odrive(self.odrive_board0)
            print("ODriveBoard0.")

        except Exception as e:
            print(f"Error reboot ODrive(s): {e}")

odrive_manager = ODriveManager()
sm = ScreenManager()
odrive_board0 = odrive_manager.odrive_board0
odrive_motor0 = odrive_manager.odrive_motor0

class MainScreen(Screen):

    def __init__(self, odrive_manager, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def test(self):
        print("TEST")

    def quit_main(self):
        try:
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp(odrive_manager=odrive_manager).stop()

    def reboot(self):
        try:
            self.odrive_manager.odrive_motor0.set_pos(2)
            self.odrive_manager.odrive_motor0.wait_for_motor_to_stop()
            dpea_odrive.odrive_helpers.reboot_odrive(self.odrive_manager.odrive_motor0)
            print("ODriveBoard0.")
            Clock.schedule_once(lambda dt:self.odrive_manager.initalize_and_cch(), 10)

        except Exception as e:
            print(f"Error rebooting: {e}")

sm.add_widget(MainScreen(name = 'main', odrive_manager=odrive_manager))

try:
    MyApp(odrive_manager=odrive_manager).run()
except Exception as e:
    odrive_manager.safe_shutdown()
    raise e