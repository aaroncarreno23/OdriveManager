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

    def build(self):
        self.title = "class ODriveManager"
        self.odrive_manager = None
        sm = ScreenManager()
        sm.add_widget(SerialInputScreen(name='serial'))
        sm.add_widget(MainScreen(name='main', odrive_manager=None))
        sm.add_widget(SlidersScreen(name='sliders_screen', odrive_manager=None))
        sm.add_widget(ButtonsScreen(name='buttons_screen', odrive_manager=None))
        sm.add_widget(InputsScreen(name='inputs_screen', odrive_manager=None))
        return sm

class SerialInputScreen(Screen):
    def save_serial(self):
        serial = self.ids.serial_input.text.strip()
        axis_text = self.ids.axis_spinner.text
        axis_num = 0 if axis_text == "Axis 0" else 1
        if serial:
            print(f"Odrive {serial} found...")
            sleep(1)
            print(f"Connecting to {serial}...")
            try:
                new_manager = ODriveManager(serial_number=serial, axis_number=axis_num)
                if new_manager.odrive_board:
                    print("Connection Successful")
                    App.get_running_app().odrive_manager = new_manager
                    self.manager.get_screen('main').odrive_manager = new_manager
                    self.manager.get_screen('sliders_screen').odrive_manager = new_manager
                    self.manager.get_screen('buttons_screen').odrive_manager = new_manager
                    self.manager.get_screen('inputs_screen').odrive_manager = new_manager
                    self.manager.current = 'main'
                else:
                    print("Could not find ODrive. Check connection/serial.")

            except Exception as e:
                print(f"Error during connection: {e}")


class ODriveManager:
    def __init__(self, serial_number=None, axis_number=0):
        self.serial_number = serial_number
        self.odrive_board = None
        self.odrive_motor = None
        try:
            self.axis_number = int(str(axis_number).replace("Axis ", ""))
        except:
            self.axis_number = 0
        if self.serial_number:
            self.initialize_odrives()
            #self.reboot()
            #self.initialize_odrives()
            if self.odrive_board and self.odrive_motor:
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
        self.odrive_motor.set_pos(5)
        print("Shutting down ODriveManager")

    def initialize_odrives(self):
        try:
            self.odrive_board = find_odrive(serial_number=self.serial_number)
            self.odrive_board.config.enable_brake_resistor = True
            print("Break resistor has been enabled")
            assert self.odrive_board.config.enable_brake_resistor is True, "Check faulty brake resistor."
            if self.axis_number == 0:
                print("Axis 0")
                self.odrive_motor = ODriveAxis(self.odrive_board.axis0)
            else:
                print("Axis 1")
                self.odrive_motor = ODriveAxis(self.odrive_board.axis1)

            print("Odrive initialized successfully")
            #print("Digital inputs:")
            #print(digital_read(self.odrive_board0, 2))
        except Exception as e:
            print(f"Error initalizing ODrive(s): {e}")

    def configure_calibrate_home_odrives(self):
        try:
            self.odrive_motor.set_vel_gain(0.05)
            self.odrive_motor.axis.controller.config.pos_gain = 20
            self.odrive_motor.axis.motor.config.torque_lim = 10
            self.odrive_motor.set_calibration_current(10)
            self.odrive_motor.set_vel_limit(4)
            print("ODrive configuration completed.")

            if not self.odrive_motor.is_calibrated():
                print("calibrating OdriveMotor...")
                self.odrive_motor.calibrate()
            self.odrive_motor.wait_for_motor_to_stop()
            print("ODriveMotor calibration completed.")

            print("Homing ODriveMotor...")
            self.odrive_motor.home_with_endstop(2,0,2)
            self.odrive_motor.wait_for_motor_to_stop()
            self.odrive_motor.set_home()
            self.odrive_motor.set_pos(1)
            print("ODrive homing completed.")

        except Exception as e:
            print(f"Error setting ODrive(s): {e}")

    def home(self):
        print("Homing ODriveMotor...")
        self.odrive_motor.home_with_endstop(2, 0, 2)
        self.odrive_motor.wait_for_motor_to_stop()
        self.odrive_motor.set_home()
        self.odrive_motor.set_pos(1)
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
            odrive_helpers_2.reboot_odrive(self.odrive_board)
            print("ODriveBoard.")
        except Exception as e:
            print(f"Error reboot ODrive(s): {e}")

class MainScreen(Screen):

    def __init__(self, odrive_manager, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def test(self):
        print("TEST")

    def quit_main(self):
        try:
            self.odrive_manager.odrive_motor.set_pos(5)
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp().stop()

    def to_sliders(self):
        self.manager.current = "sliders_screen"
        return

    def to_buttons(self):
        self.manager.current = "buttons_screen"
        return

    def to_inputs(self):
        self.manager.current = "inputs_screen"
        return

class InputsScreen(Screen):
    def __init__(self, odrive_manager, **kwargs):
        super(InputsScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def somting(self):
        pass

    def to_menu(self):
        self.manager.current = "main"
        return

    def quit_main(self):
        try:
            self.odrive_manager.odrive_motor.set_pos(5)
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp().stop()

class SlidersScreen(Screen):

    def __init__(self, odrive_manager, **kwargs):
        super(SlidersScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def set_torque_value(self, slider, value):
        torque_value = value
        self.ids.torque_lim_label.text = f"Torque Limit: {value}"
        self.odrive_manager.odrive_motor.axis.motor.config.torque_lim = torque_value
        print(f"Torque Limit: {value}")

    def set_pos(self, slider, value):
        pos_value = value
        self.ids.pos_label.text = f"Pos: {value: .1f}"
        self.odrive_manager.odrive_motor.set_pos(pos_value)
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
        self.manager.current = "main"
        return

    def quit_main(self):
        try:
            self.odrive_manager.odrive_motor.set_pos(5)
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp().stop()

class ButtonsScreen(Screen):

    def __init__(self, odrive_manager, **kwargs):
        super(ButtonsScreen, self).__init__(**kwargs)
        self.odrive_manager = odrive_manager

    def reboot(self):
        try:
            self.odrive_manager.odrive_motor.set_pos(5)
            sleep(1)
            self.odrive_manager.odrive_motor.wait_for_motor_to_stop()
            Clock.schedule_once(lambda dt: self.odrive_manager.initialize_and_cch(), 10)
            odrive_helpers_2.reboot_odrive(self.odrive_manager.odrive_board)
            print("OdriveBoard.")
            #Clock.schedule_once(lambda dt: self.odrive_manager.initialize_and_cch(), 10)

        except Exception as e:
            print(f"Error rebooting: {e}")

    def digital_read_pin(self):
        try:
            print(digital_read(self.odrive_manager.odrive_board, 2))
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
            if not self.odrive_manager.odrive_motor.is_calibrated():
                print("calibrating odrive...")
                self.odrive_manager.odrive_motor.calibrate()
            self.odrive_manager.odrive_motor.wait_for_motor_to_stop()
            self.odrive_manager.odrive_motor.motor.config.pre_calibrated = True
            self.odrive_manager.odrive_motor.config.startup_encoder_offset_calibration = True
            self.odrive_manager.odrive_motor.config.startup_closed_loop_control = True
            self.odrive_manager.odrive_motor.save_configuration()
            print("odrive PRE-CALIBRATED")
        except Exception as e:
            print(f"Error during pre-calibration {e}")

    def save_config(self):
        self.odrive_manager.save_configuration()

    def blank(self):
        pass

    def idle(self):
        self.odrive_manager.odrive_board.odrive_motor.requested_state = AxisState.IDLE

    def to_menu(self):
        self.manager.current = "main"
        return

    def quit_main(self):
        try:
            self.odrive_manager.odrive_motor.set_pos(5)
            print("ODrives getting put to sleep...")
        finally:
            print("Exiting App...")
            MyApp().stop()

if __name__ == '__main__':
    try:
        MyApp().run()
    except Exception as e:
        print(f"Critical Error: {e}")

        """
        make so you can disconnect odrive then go back to first screen
        and type new odrive to connect to. 
        
        add more/necessary sliders and buttons.
        
        
        """

#print error and clear error button

#Break position
#<odrv>.<axis>.requested_state = AXIS_STATE_IDLE

#Set pre-calibration
#<odrv>.<axis>.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
#<odrv>.<axis>.motor.config.pre_calibrated = True
#<odrv>.<axis>.config.startup_encoder_offset_calibration = True
#<odrv>.<axis>.config.startup_closed_loop_control = True
#<odrv>.save_configuration()