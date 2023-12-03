import fnmatch
import logging
import os
import re
import time

from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.DeviceUtils import DeviceUtils
from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintPrintingSelection(*args)


class CoPrintPrintingSelection(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.update_timeout = None
        self.device = None
        self.selected = None

        self.device_utils = DeviceUtils(120, self.new_device_detected)
        #self.printers = self._config.get_printers()
        #print("Printers: ", self.printers)

        initHeader = InitHeader(
            self,
            _('Connect Your 3D Printer'),
            _('Connect your 3D printer to Co Print Smart using a USB cable.'),
            "yazicibaglama"
        )

        self.image = self._gtk.Image("printer-connect", self._gtk.content_width * .3, self._gtk.content_height * .3)

        self.continueButton = Gtk.Button(_('Searching for Printer..'), name="flat-button-yellow")
        self.continueButton.connect("clicked", self.on_click_continue_button)
        self.continueButton.set_hexpand(True)
        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonBox.pack_start(self.continueButton, False, False, 0)

        spinner = Gtk.Spinner()
        spinner.props.width_request = 50
        spinner.props.height_request = 50
        spinner.start()

        backIcon = self._gtk.Image("back-arrow", 35, 35)
        backLabel = Gtk.Label(_("Back"), name="bottom-menu-label")
        backButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        backButtonBox.set_halign(Gtk.Align.CENTER)
        backButtonBox.set_valign(Gtk.Align.CENTER)
        backButtonBox.pack_start(backIcon, False, False, 0)
        backButtonBox.pack_start(backLabel, False, False, 0)
        self.backButton = Gtk.Button(name="back-button")
        self.backButton.add(backButtonBox)
        self.backButton.connect("clicked", self.on_click_back_button, 's3dp_flash_mode_selection')
        self.backButton.set_always_show_image(True)
        mainBackButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mainBackButtonBox.pack_start(self.backButton, False, False, 0)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main.pack_start(mainBackButtonBox, False, False, 0)
        main.pack_start(initHeader, False, False, 0)
        main.pack_start(self.image, False, False, 20)
        main.pack_end(buttonBox, True, False, 10)
        main.pack_end(spinner, False, False, 0)

        self.content.add(main)
        self.content.show_all()

        if self.update_timeout is None:
            self.update_timeout = GLib.timeout_add_seconds(5, self.load_devices)

        self.initialized = True

    def load_devices(self):
        if self.initialized:
            # refresh the Wi-Fi list
            spinner = Gtk.Spinner()
            spinner.props.width_request = 100
            spinner.props.height_request = 100
            spinner.start()
            self.content.show_all()
            GLib.idle_add(self.device_utils.wait_for_new_devicez)

    def new_device_detected(self, device):
        self.device = device
        self.device_utils.stop()
        time.sleep(1)
        # todo display
        self._screen.show_panel(
            "co_print_printing_selection_port",
            "co_print_printing_selection_port",
            None,
            remove=2,
            device=self.device
        )

    def initialize(self, device_utils=None):
        pass

    def on_click_continue_button(self, continueButton):
        print("click")

    def on_click_back_button(self, button, data):
        self._screen.show_panel(data, data, None, 1)
