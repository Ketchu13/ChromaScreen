import json
import logging
import os
import re

from ks_includes.DeviceUtils import DeviceUtils
from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
from ks_includes.widgets.usbSerial import DeviceCard

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintPrintingSelectionPort(*args)


class CoPrintPrintingSelectionPort(ScreenPanel):
    initialized = False
    device_utils: DeviceUtils

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.update_timeout = False
        initHeader = InitHeader(
            self,
            _('Connect Your 3D Printer'),
            _('Connect your 3D printer to Co Print Smart using a USB cable.'),
            "yazicibaglama"
        )

        new_menu_items = []

        menu_items = new_menu_items
        self.contentBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.contentBox.set_hexpand(True)
        self.contentBox.set_halign(Gtk.Align.CENTER)

        self.leftBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.rightBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.rightBox.set_hexpand(True)

        self.selectedDevice = None

        # //---------Left Side---------//
        self.leftScroll = self._gtk.ScrolledWindow()
        self.leftScroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.leftScroll.set_min_content_height(self._screen.height * .3)
        self.leftScroll.set_kinetic_scrolling(True)
        self.leftScroll.get_overlay_scrolling()
        #self.leftScroll.set_margin_left(self._gtk.action_bar_width * 1)
        #self.leftScroll.set_margin_right(self._gtk.action_bar_width * 1)
        self.leftScroll.add(self.leftBox)
        self.contentBox.pack_start(self.leftScroll, False, False, 0)
        self.leftScroll.set_size_request(200,200)
        # //---------Right Side---------//
        self.alpha_DescriptionLabel = Gtk.Label('', name="contract-approval-label")
        self.alpha_DescriptionLabel.set_line_wrap(True)
        self.alpha_DescriptionLabel.set_max_width_chars(200)
        self.alpha_DescriptionLabel.set_hexpand(True)
        self.rightBox.pack_start(self.alpha_DescriptionLabel, True, True, 0)

        self.rightScroll = self._gtk.ScrolledWindow()
        self.rightScroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.rightScroll.set_min_content_height(self._screen.height * .3)
        self.rightScroll.set_kinetic_scrolling(True)
        self.rightScroll.get_overlay_scrolling()
        #self.rightScroll.set_margin_left(self._gtk.action_bar_width * 1)
        #self.rightScroll.set_margin_right(self._gtk.action_bar_width * 1)
        self.rightScroll.add(self.rightBox)
        self.contentBox.pack_start(self.rightScroll, True, True, 0)
        self.rightScroll.set_size_request(800, 400)

        self.continueButton = Gtk.Button(_('Continue'), name="flat-button-blue")
        self.continueButton.connect("clicked", self.on_click_continue_button)
        self.continueButton.set_hexpand(True)
        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonBox.pack_start(self.continueButton, False, False, 0)

        backIcon = self._gtk.Image("back-arrow", 35, 35)
        backLabel = Gtk.Label(_("Back"), name="bottom-menu-label")

        backButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        backButtonBox.set_halign(Gtk.Align.CENTER)
        backButtonBox.set_valign(Gtk.Align.CENTER)
        backButtonBox.pack_start(backIcon, False, False, 0)
        backButtonBox.pack_start(backLabel, False, False, 0)

        self.backButton = Gtk.Button(name="back-button")
        self.backButton.add(backButtonBox)
        self.backButton.connect(
            "clicked",
            self.on_click_back_button,
            'co_print_printing_selection'
        )
        self.backButton.set_always_show_image(True)

        mainBackButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mainBackButtonBox.pack_start(self.backButton, False, False, 0)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        main.pack_start(mainBackButtonBox, False, False, 0)
        main.pack_start(initHeader, False, False, 0)
        main.pack_start(self.contentBox, True, True, 10)
        main.pack_end(buttonBox, False, False, 10)

        self.content.add(main)
        GLib.idle_add(self.reload_devices_port)

        if self.update_timeout is None:
            self.update_timeout = GLib.timeout_add_seconds(5, self.reload_devices_port)

        self.initialized = True

    def initialize(self, device_utils,  device=None):
        self.device_utils = device_utils if device_utils else DeviceUtils(120, self.new_device_detected)
        self.selectedDevice = device
        print(self.device_utils)
        print(self.selectedDevice)

        print("initialized")

    def on_click_callback(self, widget, event, device, devlink):
        print(widget)
        print(event)
        print(device)
        self.selectedDevice = device
        selectedDevice = self.device_utils.get_deviceDict_by_devlink(devlink)
        print(selectedDevice)
        self.alpha_DescriptionLabel.set_text(json.dumps(selectedDevice, indent=4))

    def reload_devices_port(self):
        print(self.selectedDevice)
        if self.initialized:

            for item in self.leftScroll.get_children():
                self.leftScroll.remove(item)
            self.leftBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)  # , hexpand=True)
            self.devices = self.get_serial_devices_path()
            menu_items = self.devices  # get /dev/serial/by-path
            for menu_item in menu_items:
                buttonStyle = "flat-button-black"
                devlinks = self.selectedDevice["DEVLINKS"]
                match_devbypath = re.search(r'/dev/serial/by-path/(\S+)', devlinks)
                device = self.device_utils.get_deviceDict_by_devlink(menu_item["Name"])
                print(device)
                if device:
                    if match_devbypath:
                        devlink = match_devbypath.group(1)
                        print(menu_item["Name"], devlink)
                        if menu_item["Name"] == devlink:
                            print("ok")
                            buttonStyle = "flat-button-green2"

                            self.alpha_DescriptionLabel.set_text(json.dumps(device, indent=4))
                    devicecard = DeviceCard(
                        self,
                        device,
                        menu_item["Name"]
                    )
                    self.leftBox.pack_start(devicecard, False, False, 0)

            self.leftScroll.add(self.leftBox)
            self.leftScroll.show_all()

    @staticmethod
    def get_serial_devices_path():
        # ls /dev/serial/by-path
        try:
            device_path = os.listdir("/dev/serial/by-path")
        except Exception as e:
            logging.error(e)
            return None
        devices_paths = []
        for device in device_path:
            devices_paths.append({"Name": device, "path": "/dev/serial/by-path/%s" % device})
        return devices_paths

    def new_device_detected(self, devices, device=None):
        print(device)
        print(devices)

    def on_click_continue_button(self, continueButton):
        self._screen.show_panel("co_print_printing_brand_selection", "co_print_printing_brand_selection", None, 2)

    def on_click_back_button(self, button, data):
        self._screen.show_panel(data, data, None, 2, device_utils=None)
