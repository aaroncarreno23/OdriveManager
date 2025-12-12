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
from kivy.uix.textinput import TextInput
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

import odrive_helpers_2
from odrive_helpers_2 import *
from odrive_helpers_2 import digital_read
from pidev.kivy.PassCodeScreen import PassCodeScreen
from pidev.kivy.PauseScreen import PauseScreen

Builder.load_file('main.kv')
print("main.kv loaded.")
Builder.load_file('sliders.kv')
print("sliders.kv loaded.")
Builder.load_file('buttons.kv')
print("buttons.kv loaded.")
Builder.load_file('inputs.kv')
print("inputs.kv loaded.")
Builder.load_file('serial.kv')
print("serial.kv loaded.")

Window.clearcolor = (0.4, 0.5, 0.2, 1) #white

"208E3388304B"

class MyApp(App):

    def __init__(self, odrive_manager, **kwargs):
        super(MyApp, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def build(self):
        self.title = "class ODriveManager"
        return sm

class SerialInputScreen(Screen):
    def save_serial(self):
        serial = self.ids.serial_input.text.strip()
        if serial:
            self.manager.odrive_manager = ODriveManager(serial)
            self.manager.current = 'main_screen'


class ODriveManager:
    def __init__(self, serial_number=None):
        self.serial_number = serial_number
        self.odrive_board0 = None
        self.odrive_motor1 = None
        self.initialize_odrives()
        self.reboot()
        self.initialize_odrives()
        if self.odrive_board0 and self.odrive_motor1:
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
        self.odrive_motor1.set_pos(5)
        print("Shutting down ODriveManager")

    def initialize_odrives(self):
        try:
            odrv0 = self.serial_number
            self.odrive_board0 = find_odrive(odrv0)
            self.odrive_board0.config.enable_brake_resistor = True
            print("Break resistor has been enabled")
            assert self.odrive_board0.config.enable_brake_resistor is True, "Check faulty brake resistor."
            self.odrive_motor1 = ODriveAxis(self.odrive_board0.axis0)
            print("Odrive initialized successfully")
            #print("Digital inputs:")
            #print(digital_read(self.odrive_board0, 2))
        except Exception as e:
            print(f"Error initalizing ODrive(s): {e}")

    def configure_calibrate_home_odrives(self):
        try:
            self.odrive_motor1.set_vel_gain(0.05)
            self.odrive_motor1.axis.controller.config.pos_gain = 20
            self.odrive_motor1.axis.motor.config.torque_lim = 10
            self.odrive_motor1.set_calibration_current(10)
            self.odrive_motor1.set_vel_limit(4)
            print("ODrive configuration completed.")

            if not self.odrive_motor1.is_calibrated():
                print("calibrating OdriveMotor0...")
                self.odrive_motor1.calibrate()
            self.odrive_motor1.wait_for_motor_to_stop()
            print("ODriveMotor0 calibration completed.")

            print("Homing ODriveMotor0...")
            self.odrive_motor1.home_with_endstop(2,0,2)
            self.odrive_motor1.wait_for_motor_to_stop()
            self.odrive_motor1.set_home()
            self.odrive_motor1.set_pos(1)
            print("ODrive homing completed.")

        except Exception as e:
            print(f"Error setting ODrive(s): {e}")

    def home(self):
        print("Homing ODriveMotor0...")
        self.odrive_motor1.home_with_endstop(2, 0, 2)
        self.odrive_motor1.wait_for_motor_to_stop()
        self.odrive_motor1.set_home()
        self.odrive_motor1.set_pos(1)
        print("ODrive homing completed.")

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
            odrive_helpers_2.reboot_odrive(self.odrive_board0)
            print("ODriveBoard0.")
        except Exception as e:
            print(f"Error reboot ODrive(s): {e}")

odrive_manager = ODriveManager()
sm = ScreenManager()
odrive_board0 = odrive_manager.odrive_board0
odrive_motor1 = odrive_manager.odrive_motor1

class MainScreen(Screen):

    def __init__(self, odrive_manager, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def test(self):
        print("TEST")

    def quit_main(self):
        try:
            self.odrive_manager.odrive_motor1.set_pos(5)
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp(odrive_manager=odrive_manager).stop()

    def to_sliders(self):
        sm.current = "sliders_screen"
        return

    def to_buttons(self):
        sm.current = "buttons_screen"
        return

    def to_inputs(self):
        sm.current = "inputs_screen"
        return

class InputsScreen(Screen):
    def __init__(self, odrive_manager, **kwargs):
        super(InputsScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def somting(self):
        pass

    def to_menu(self):
        sm.current = "main"
        return

    def quit_main(self):
        try:
            self.odrive_manager.odrive_motor1.set_pos(5)
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp(odrive_manager=odrive_manager).stop()

class SlidersScreen(Screen):

    def __init__(self, odrive_manager, **kwargs):
        super(SlidersScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def set_torque_value(self, slider, value):
        torque_value = value
        self.ids.torque_lim_label.text = f"Torque Limit: {value}"
        self.odrive_manager.odrive_motor1.axis.motor.config.torque_lim = torque_value
        print(f"Torque Limit: {value}")

    def set_pos(self, slider, value):
        pos_value = value
        self.ids.pos_label.text = f"Pos: {value: .1f}"
        self.odrive_manager.odrive_motor1.set_pos(pos_value)
        print(f"Pos: {value: .1f}")

    def set_vel_lim(self):
        pass

    def calibration_curr(self):
        pass

    def pos_gain(self):
        pass

    def vel_gain(self):
        pass

    def resistance_calib_max_voltage(self):
        pass

    def to_menu(self):
        sm.current = "main"
        return

    def quit_main(self):
        try:
            self.odrive_manager.odrive_motor1.set_pos(5)
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp(odrive_manager=odrive_manager).stop()

class ButtonsScreen(Screen):

    def __init__(self, odrive_manager, **kwargs):
        super(ButtonsScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def reboot(self):
        try:
            self.odrive_manager.odrive_motor1.set_pos(5)
            sleep(1)
            self.odrive_manager.odrive_motor1.wait_for_motor_to_stop()
            Clock.schedule_once(lambda dt: self.odrive_manager.initialize_and_cch(), 10)
            odrive_helpers_2.reboot_odrive(self.odrive_manager.odrive_board0)
            print("OdriveBoard0.")
            #Clock.schedule_once(lambda dt: self.odrive_manager.initialize_and_cch(), 10)

        except Exception as e:
            print(f"Error rebooting: {e}")

    def digital_read_pin(self):
        try:
            print(digital_read(self.odrive_manager.odrive_board0, 2))
        except Exception as e:
            print(f"Error reading pin 2: {e}")

    def home_motor(self):
        try:
            self.odrive_manager.home()
        except Exception as e:
            print(f"Error homing ODrive(s): {e}")

    def calibrate(self):
        pass

    def pre_calibrate(self):
        try:
            if not self.odrive_manager.odrive_motor1.is_calibrated():
                print("calibrating odrive...")
                self.odrive_manager.odrive_motor1.calibrate()
            self.odrive_manager.odrive_motor1.wait_for_motor_to_stop()

            self.odrive_manager.odrive_motor1.motor.config.pre_calibrated = True
            self.odrive_manager.odrive_motor1.wait_for_motor_to_stop()
            self.odrive_manager.odrive_motor1.config.startup_encoder_offset_calibration = True
            self.odrive_manager.odrive_motor1.wait_for_motor_to_stop()
            self.odrive_manager.odrive_motor1.config.startup_closed_loop_control = True
            self.odrive_manager.odrive_motor1.wait_for_motor_to_stop()
            print("odrive PRE-CALIBRATED")
        except Exception as e:
            print(f"Error during pre-calibration {e}")

    def save_config(self):
        pass

    def blank(self):
        pass

    def idle(self):
        pass

    def to_menu(self):
        sm.current = "main"
        return

    def quit_main(self):
        try:
            self.odrive_manager.odrive_motor1.set_pos(5)
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp(odrive_manager=odrive_manager).stop()

sm.add_widget(SerialInputScreen(name = 'serial'))
sm.add_widget(MainScreen(name = 'main', odrive_manager=odrive_manager))
sm.add_widget(SlidersScreen(name = 'sliders_screen', odrive_manager=odrive_manager))
sm.add_widget(ButtonsScreen(name = 'buttons_screen', odrive_manager=odrive_manager))
sm.add_widget(InputsScreen(name = 'inputs_screen', odrive_manager=odrive_manager))

try:
    MyApp(odrive_manager=odrive_manager).run()
except Exception as e:
    odrive_manager.safe_shutdown()
    raise e

#print error and clear error button

#Break position
#<odrv>.<axis>.requested_state = AXIS_STATE_IDLE

#Set pre-calibration
#<odrv>.<axis>.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
#<odrv>.<axis>.motor.config.pre_calibrated = True
#<odrv>.<axis>.config.startup_encoder_offset_calibration = True
#<odrv>.<axis>.config.startup_closed_loop_control = True
#<odrv>.save_configuration()