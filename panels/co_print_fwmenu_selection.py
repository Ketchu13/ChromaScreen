import json
import logging
import os
import subprocess

from gi.overrides import GdkPixbuf

from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintChipSelection(*args)


class CoPrintChipSelection(ScreenPanel):
    mcu_arch_names = {
        "Atmega AVR": "MACH_AVR",
        "SAM 3 / 4 / E70": "MACH_ATSAM",
        "SAM D21 / SAM D51": "MACH_ATSAMD",
        "LPC176X": "MACH_LPC176X",
        "STM 32": "MACH_STM32",
        "Raspberry PI RP2040": "MACH_RP2040",
        "Beaglebone PRU": "MACH_PRU",
        "Linux Procces": "MACH_LINUX",
        "Host simulator": "MACH_HOST_SIM"
    }
    def get_lowlevel_options(self, architecture, mcu_model):
        # load json file
        fw_configs = None
        try:
            with open(self.fw_configs_path, "r") as f:
                fw_configs = json.load(f)
        except Exception as e:
            logging.error("Error while loading fwconfig.json: %s", e)
            return None
        if fw_configs is None:
            return None
        # get mcu models for the selected architecture from ./fwconfig.json
        lowlevel_options_tmp = None
        formated_arch_name = self.mcu_arch_names[architecture]
        if formated_arch_name in fw_configs["mcus"]:
            current_arch_data = fw_configs["mcus"][formated_arch_name]
            if "low-level" in current_arch_data:
                lowlevel_options_tmp = current_arch_data["low-level"]
        lowlevel_options = []
        if lowlevel_options_tmp is not None:
            for lowlevel_option in lowlevel_options_tmp:
                lowlevel_options.append(lowlevel_option)
        return lowlevel_options
     
    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.fw_configs_path = os.path.join(os.path.dirname(__file__), "fwconfig", "fwconfig.json")

        self.low_level_options = None
        self.selected = None
        self.architecture_selected = None
        self.mcu_model_selected = None

        panel = {
            "title": _("Klipper Firmware Configuration"),
            "name": "co_print_fwmenu_selection",
            "icon": "chip",
            "text": _("Please select the architecture, communication frequency, clock speed and model of the chip you will be using."),
            "next_panel": "co_print_mcu_selection",
            "previous_panel": "co_print_wifi_selection"
        }

        menu_items = [
            {'Name': _("MCU Architecture")  , 'key': 'architecture'     , "panel_link": "co_print_mcu_selection"},
            {'Name': _("Processor Model")   , 'key': 'model'            , "panel_link": "co_print_mcu_model_selection"},
        ]
        menu_items_low_level = [
            {'Name': _("Botloader Offset"), 'key': 'bootloader', "panel_link": "co_print_mcu_bootloader_ofset"},
            {'Name': _("Com Interface")     , 'key': 'com_interface'    , "panel_link": "co_print_mcu_com_interface"},
            {'Name': _("Clock Referance")   , 'key': 'clock_reference'  , "panel_link": "co_print_mcu_clock_reference"},
            {'Name': _("USB ids")           , 'key': 'usb_ids'          , "panel_link": "co_print_mcu_usb_ids"}
        ]

        self.menu_items = menu_items

        initHeader = InitHeader(self, panel['title'], panel['text'], panel['icon'])

        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}
        if "low_level" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["low_level"] = False
        self.low_level_enabled = self._screen._fw_config["mcu"]["low_level"]

        if "model" in self._screen._fw_config["mcu"]:
            self.mcu_model_selected = self._screen._fw_config["mcu"]["model"]
        if "architecture" in self._screen._fw_config["mcu"]:
            self.architecture_selected = self._screen._fw_config["mcu"]["architecture"]
            self.low_level_options = self.get_lowlevel_options(self._screen._fw_config["mcu"]["architecture"], None)

        # if option name is in low-level options
        if self.low_level_options is not None:
            for menu_item_ll in menu_items_low_level:
                if menu_item_ll['key'] in self.low_level_options:
                    if self.architecture_selected is not None:
                        if self.mcu_model_selected is not None:
                            if self.low_level_enabled:
                                menu_items.append(menu_item_ll)

        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        for menu_item in menu_items:
            menu_item_value = "..."
            menu_item_name = menu_item['Name']


            if (menu_item['key'] in self._screen._fw_config["mcu"] and
                    self._screen._fw_config["mcu"][menu_item['key']] is not None and
                    len(self._screen._fw_config["mcu"][menu_item['key']]) > 1):
                menu_image_name = "approve"
                menu_item_value = self._screen._fw_config["mcu"][menu_item['key']]
            else:
                menu_image_name = "support"

            menu_item_image = self._gtk.Image(
                menu_image_name,
                self._gtk.content_width * .03,
                self._gtk.content_height * .03
            )

            current_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            menu_name_label = Gtk.Label(menu_item_name)
            menu_name_label.set_alignment(0, 0.5)
            menu_name_label.set_width_chars(30)
            current_row.pack_start(menu_name_label, False, False, 0)

            menu_value_label = Gtk.Label(menu_item_value)
            menu_value_label.set_width_chars(20)
            menu_value_label.set_justify(Gtk.Justification.LEFT)
            current_row.pack_start(menu_value_label, False, False, 0)

            current_row.pack_start(menu_item_image, False, False, 0)

            menu_button_edit = Gtk.Button(label="Edit", name="flat-button-blue", hexpand=True)
            menu_button_edit.set_size_request(20, 20)
            menu_button_edit.connect("clicked", self.on_click_menu_item_edit, menu_item['panel_link'])

            current_row.pack_start(menu_button_edit, False, False, 0)
            current_row.get_style_context().add_class("fw-menu-treeview-row")
            self.mainBox.pack_start(current_row, False, False, 0)


        # TODO: Add config and : add isb ids and show hide if low level enable/disable

        self.checkButton = CheckButtonBox(
            self,
            _('Enable extra low-level configuration options'),
            self.lowLevel_on_check,
            self._screen._fw_config["mcu"]["low_level"]
        )

        checkButtonBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        checkButtonBox.set_halign(Gtk.Align.CENTER)
        checkButtonBox.set_valign(Gtk.Align.CENTER)
        checkButtonBox.pack_start(self.checkButton, False, False, 0)
        checkButtonBox.set_center_widget(self.checkButton)

        self.continueButton = Gtk.Button(_('Continue'), name="flat-button-blue")
        self.continueButton.connect("clicked", self.on_click_continue_button)
        self.continueButton.set_hexpand(True)

        self.wizardButton = Gtk.Button(_('Start Wizard'), name="flat-button-blue")
        self.wizardButton.connect("clicked", self.on_click_wizzard_button)
        self.wizardButton.set_hexpand(True)

        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonBox.pack_start(self.continueButton, False, False, 0)
        buttonBox.pack_start(self.wizardButton, False, False, 0)

        backIcon = self._gtk.Image("back-arrow", 35, 35)
        backLabel = Gtk.Label(_("Back"), name="bottom-menu-label")

        backButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        backButtonBox.set_halign(Gtk.Align.CENTER)
        backButtonBox.set_valign(Gtk.Align.CENTER)
        backButtonBox.pack_start(backIcon, False, False, 0)
        backButtonBox.pack_start(backLabel, False, False, 0)

        self.backButton = Gtk.Button(name ="back-button")
        self.backButton.add(backButtonBox)
        self.backButton.connect("clicked", self.on_click_back_button, 'co_print_wifi_selection')
        self.backButton.set_always_show_image(True)

        mainBackButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mainBackButtonBox.pack_start(self.backButton, False, False, 0)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main.set_halign(Gtk.Align.CENTER)
        main.pack_start(initHeader, False, False, 0)
        main.pack_start(self.mainBox, True, True, 0)
        main.pack_end(buttonBox, False, False, 10)
        main.pack_end(checkButtonBox, False, False, 10)
        
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.pack_start(mainBackButtonBox, False, False, 0)
        page.pack_start(main, True, True, 0)
      
        self.content.add(page)
        self._screen.base_panel.visible_menu(False)

    def lowLevel_on_check(self, val):
        self._screen._fw_config["mcu"]["low_level"] = val
        self._screen.show_panel("co_print_fwmenu_selection", "co_print_fwmenu_selection", None, 2)

    def on_click_menu_item_edit(self, button, target_panel):
        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}
        self._screen._fw_config["mcu"]["manual_cfg"] = True
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def on_click_continue_button(self, continueButton, target_panel=None):
        pass

    def on_click_wizzard_button(self, continueButton):
        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}
        self._screen.show_panel("co_print_mcu_selection", "co_print_mcu_selection", None, 2)

    def on_click_back_button(self, button, target_panel):
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def _resolve_radio(self, master_radio):
        active = next((
            radio for radio in
            master_radio.get_group()
            if radio.get_active()
        ))
        return active

