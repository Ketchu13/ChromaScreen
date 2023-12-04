import json
import logging
import os
from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
from ks_includes.widgets.usbIDsCard import UsbIdCard

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintMcuUsbIds(*args)


class CoPrintMcuUsbIds(ScreenPanel):

    option_checked: bool

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.usb_ids = None
        self.option_checked = False
        self.selected = None
        self.usbbIdsCards = []

        self.usb_ids = [
            {'desc': "USB vendor ID", 'type': 'vendor', 'id': '0x1d50', 'id_default': '0x1d50'},
            {'desc': "USB device ID", 'type': 'device', 'id': '0x614e', 'id_default': '0x614e'},
        ]
        #  self._screen._fw_config["mcu"]["manual_cfg"] = True
        # get fw_config from screen to know if we are in manual or wizzard config
        validate_button = {
            "panel_link": "co_print_fwmenu_selection",
            "panel_link_b": "co_print_fwmenu_selection",
            "text": _('Save')
        }
        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}

        if "usb_ids" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["usb_ids"] = {}

        if "serial_from" not in self._screen._fw_config["mcu"]["usb_ids"]:
            self._screen._fw_config["mcu"]["usb_ids"]["serial_from"] = False

        if "vendor" not in self._screen._fw_config["mcu"]["usb_ids"]:
            self._screen._fw_config["mcu"]["usb_ids"]["vendor"] = self.usb_ids[0]["id_default"]
        if "device" not in self._screen._fw_config["mcu"]["usb_ids"]:
            self._screen._fw_config["mcu"]["usb_ids"]["device"] = self.usb_ids[1]["id_default"]

        initHeader = InitHeader(
            self,
            _('USB IDS'),
            _('Set the usb ids that you will use to identify your board. Use default values if you are not sure.'),
            "mikrochip"
        )

        usbIdsflowbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, halign=Gtk.Align.CENTER)
        usbIdsflowbox.set_hexpand(True)

        for usb_id in self.usb_ids:
            # check if data exists in fw_config
            if usb_id["type"] in self._screen._fw_config["mcu"]["usb_ids"]:
                usb_id["id"] = self._screen._fw_config["mcu"]["usb_ids"][usb_id["type"]]
            usb_idCard = UsbIdCard(self, usb_id)
            usbIdsflowbox.pack_start(usb_idCard, False, False, 0)
            self.usbbIdsCards.append(usb_idCard)

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_min_content_height(self._screen.height * .3)
        self.scroll.set_kinetic_scrolling(True)
        self.scroll.get_overlay_scrolling()
        self.scroll.set_margin_left(self._gtk.action_bar_width * 1)
        self.scroll.set_margin_right(self._gtk.action_bar_width * 1)
        self.scroll.add(usbIdsflowbox)
        self.scroll.set_halign(Gtk.Align.CENTER)
        self.scroll.set_valign(Gtk.Align.CENTER)

        self.checkButton = CheckButtonBox(self, _('USB serial number from CHIPID'), self.onCheck)
        self.checkButton.set_hexpand(True)
        self.checkButton.set_margin_left(self._gtk.action_bar_width * 3)
        self.checkButton.set_margin_right(self._gtk.action_bar_width * 3)
        self.checkButton.set_active(self._screen._fw_config["mcu"]["usb_ids"]["serial_from"])

        checkButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        checkButtonBox.pack_start(self.checkButton, False, True, 0)
        checkButtonBox.set_homogeneous(True)
        checkButtonBox.set_halign(Gtk.Align.CENTER)
        checkButtonBox.set_valign(Gtk.Align.CENTER)

        self.continueButton = Gtk.Button(validate_button["text"], name="flat-button-blue", hexpand=True)
        self.continueButton.connect("clicked", self.on_click_continue_button, validate_button["panel_link"])

        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonBox.pack_start(self.continueButton, False, False, 0)
        buttonBox.set_center_widget(self.continueButton)

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
        self.backButton.connect("clicked", self.on_click_back_button, validate_button["panel_link_b"])
        self.backButton.set_always_show_image(True)

        mainBackButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mainBackButtonBox.pack_start(self.backButton, False, False, 0)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, halign=Gtk.Align.CENTER)
        main.pack_start(initHeader, False, False, 0)
        main.pack_start(self.scroll, True, True, 0)
        main.pack_end(buttonBox, True, False, 10)
        main.pack_end(checkButtonBox, False, True, 5)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.pack_start(mainBackButtonBox, False, False, 0)
        page.pack_start(main, True, True, 0)

        self.content.add(page)
        # self._screen.base_panel.visible_menu(False)

    def onCheck(self, active):
        # save to fw_config
        self.option_checked = active

    def on_click_continue_button(self, continueButton, target_panel=None):
        config_ok = True
        usb_ids_result = {}
        for usb_idCard in self.usbbIdsCards:
            if usb_idCard._on_check_button_clicked(None):
                usb_ids_result[usb_idCard.usb_id["type"]] = usb_idCard.usb_id["id"]
            else:
                config_ok = False
        if config_ok:
            if "mcu" not in self._screen._fw_config:
                self._screen._fw_config["mcu"] = {}

            # save to fw_config
            self._screen._fw_config["mcu"]["usb_ids"] = usb_ids_result
            self._screen._fw_config["mcu"]["usb_ids"]["serial_from"] = self.option_checked
            # open target panel
            self._screen.show_panel(target_panel, target_panel, None, 2)

    def on_click_back_button(self, button, target_panel):
        self._screen.show_panel(target_panel, target_panel, None, 2)
