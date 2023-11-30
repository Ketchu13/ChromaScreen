import logging
import os
from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintSdCardSelectionProcessWaiting(*args)


class CoPrintSdCardSelectionProcessWaiting(ScreenPanel):


    def __init__(self, screen, title):
        super().__init__(screen, title)


        self.sdcard_utils = None

        initHeader = InitHeader(
            self,
            _('Writing to SD Card'),
            _('Insert the SD Card of your printer into ChromaPad to change the program of your 3D printer.'),
            "sdkart"
        )

        self.image = self._gtk.Image("usb-wait", self._gtk.content_width * .4, self._gtk.content_height * .4)

        self.continueButton = Gtk.Button(_('Please insert the USB drive.'), name="flat-button-yellow")
        self.continueButton.connect("clicked", self.on_click_continue_button)
        self.continueButton.set_hexpand(True)
        self.continueButton.set_margin_left(self._gtk.action_bar_width *3)
        self.continueButton.set_margin_right(self._gtk.action_bar_width*3)

        self.continueButtonExplicit = Gtk.Button(_("Continue"), name="flat-button-blue", hexpand=True)
        self.continueButtonExplicit.connect("clicked", self.on_click_continue_button)

        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonBox.pack_start(self.continueButton, False, False, 0)
        buttonBox.set_center_widget(self.continueButton)

        buttonBoxExplicit = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonBoxExplicit.pack_start(self.continueButtonExplicit, False, False, 0)
        buttonBoxExplicit.set_center_widget(self.continueButtonExplicit)

        backIcon = self._gtk.Image("back-arrow", 35, 35)
        backLabel = Gtk.Label(_("Back"), name="bottom-menu-label")

        backButtonBox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=0,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER
        )
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
        main.pack_start(self.image, True, True, 25)
        main.pack_end(buttonBoxExplicit, True, False, 5)
        main.pack_end(buttonBox, True, False, 15)
        GLib.idle_add(self.wait_for_sdcard)
        self.content.add(main)

    def wait_for_sdcard(self):
        self.new_device_detected(self.sdcard_utils.wait_for_new_device())

    def new_device_detected(self, device):
        self._screen.show_panel("co_print_sd_card_selection_process", "co_print_sd_card_selection_process", None, 2, sdcard_utils=self.sdcard_utils)

    def initialize(self, sdcard_utils):
        self.sdcard_utils = sdcard_utils

    def on_click_continue_button(self, continueButton):
        self._screen.show_panel("co_print_sd_card_selection_process", "co_print_sd_card_selection_process", None, 2, sdcard_utils=self.sdcard_utils)

    def on_click_back_button(self, button, data):
        self._screen.show_panel(data, data, None, 2)
