import json
import logging
import os
import re

from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintMcuComInterface(*args)


class CoPrintMcuComInterface(ScreenPanel):
    def get_communication_interface(self, architecture, mcu_model):
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
        mcu_comm_interfaces_tmp = []
        formated_arch_name = architecture["key"]
        if formated_arch_name in fw_configs["mcus"]:
            current_arch_data = fw_configs["mcus"][formated_arch_name]
            if "models" in current_arch_data:
                mcu_models_tmp = current_arch_data["models"]
                if "com_interface" in current_arch_data:
                    for comm_interface in current_arch_data["com_interface"]:
                        current_comm_interface = current_arch_data["com_interface"][comm_interface]
                        mcu_model_key_name = None
                        if mcu_model["key"] in mcu_models_tmp:
                            mcu_model_key_name = mcu_model["key"]

                        if mcu_model_key_name is not None and mcu_model_key_name in current_comm_interface or "all" in current_comm_interface:
                            mcu_comm_interfaces_tmp.append(comm_interface)
        mcu_comm_interfaces = []
        if mcu_comm_interfaces_tmp is not None:
            for mcu_comm_interface in mcu_comm_interfaces_tmp:
                # format clock reference name
                new_name = mcu_comm_interface.split("_")[-1]

                mcu_comm_interfaces.append({'Name': new_name, 'key': mcu_comm_interface, 'Button': Gtk.RadioButton()})
        return mcu_comm_interfaces

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.fw_configs_path = os.path.join(os.path.dirname(__file__), "fwconfig", "fwconfig.json")

        self.selected = None
        self.architecture = None
        self.selected_mcu_model = None
        self.selected_mcu_comm_interface = None
        self.mcu_comm_interfaces = None

        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}

        if "architecture" in self._screen._fw_config["mcu"]:
            # get mcu models for the selected architecture from ./fwconfig.json
            self.architecture = self._screen._fw_config["mcu"]["architecture"]

        if "model" in self._screen._fw_config["mcu"]:
            self.selected_mcu_model = self._screen._fw_config["mcu"]["model"]

        if self.architecture is None or self.selected_mcu_model is None:
            # return to previous panel if architecture is not selected
            self._screen.show_panel("co_print_mcu_selection", "co_print_mcu_selection", None, 2)
            return

        self.mcu_comm_interfaces = self.get_communication_interface(self.architecture, self.selected_mcu_model)

        # debug
        if self.mcu_comm_interfaces is None:
            self.mcu_comm_interfaces = [
                {'Name': "USB (on PA11/PA12)"           ,  'Button': Gtk.RadioButton()},
                {'Name': "Serial (on USART1 PA10/PA9)"  ,  'Button': Gtk.RadioButton()},
                {'Name': "Serial (on USART1 PB7/PB6)"   ,  'Button': Gtk.RadioButton()},
                {'Name': "Serial (on USART2 PA3/PA2)"   , 'Button': Gtk.RadioButton()},
                {'Name': "Serial (on USART2 PD6/PD5)"   , 'Button': Gtk.RadioButton()},
                {'Name': "Serial (on USART3 PB11/PB10)" ,  'Button': Gtk.RadioButton()},
                {'Name': "Serial (on USART3 PD9/PD8)"   ,  'Button': Gtk.RadioButton()},
                {'Name': "CAN bus (on PA11/PA12)"       ,  'Button': Gtk.RadioButton()},
                {'Name': "CAN bus (on PA11/PB9)"        ,  'Button': Gtk.RadioButton()},
                {'Name': "CAN bus (on PA11/PB9)"        , 'Button': Gtk.RadioButton()}
            ]
        # end debug

        group = None

        initHeader = InitHeader(
            self,
            _('Com Interface'),
            _('Select the com interface model located on the board you will be controlling.'),
            "mikrochip"
        )

        '''diller bitis'''
        grid = Gtk.Grid(
            column_homogeneous=True,
            column_spacing=10,
            row_spacing=10
        )
        row = 0
        count = 0

        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}

        if "com_interface" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["com_interface"] = None

        for mcu_comm_interface in self.mcu_comm_interfaces:



            mcu_comm_interfaceName = Gtk.Label(mcu_comm_interface['Name'], name="wifi-label")
            mcu_comm_interfaceName.set_alignment(0, 0.5)

            # reduce font size if mcu model name is too long
            if len(mcu_comm_interface['Name']) > 30:
                mcu_comm_interfaceName.set_size_request(300, -1)
                mcu_comm_interfaceName.set_max_width_chars(30)
                mcu_comm_interfaceName.set_ellipsize(Pango.EllipsizeMode.END)

            mcu_comm_interface['Button'] = Gtk.RadioButton.new_with_label_from_widget(group, "")
            mcu_comm_interface['Button'].set_alignment(1, 0.5)
            mcu_comm_interface['Button'].connect("toggled", self.radioButtonSelected, mcu_comm_interface)

            mcu_comm_interfaceBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40, name="chip")

            f = Gtk.Frame(name="chip")

            mcu_comm_interfaceBox.pack_start(mcu_comm_interfaceName, False, True, 10)
            mcu_comm_interfaceBox.pack_end(mcu_comm_interface['Button'], False, False, 10)

            f.add(mcu_comm_interfaceBox)

            grid.attach(f, count, row, 1, 1)

            if self._screen._fw_config["mcu"]["com_interface"]:
                if self._screen._fw_config["mcu"]["com_interface"]['Name'] == mcu_comm_interface['Name']:
                    mcu_comm_interface['Button'].set_active(True)
                    self.selected = mcu_comm_interface
                    group = mcu_comm_interface['Button']

            # set group if mcu_comm_interface name is the same as the one in fw_config
            if group is None:
                group = mcu_comm_interface['Button']
                self.selected = mcu_comm_interface

            count += 1
            if count % 1 == 0:
                count = 0
                row += 1

        gridBox = Gtk.FlowBox()
        gridBox.set_halign(Gtk.Align.CENTER)
        gridBox.add(grid)

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_min_content_height(self._screen.height * .3)
        self.scroll.set_kinetic_scrolling(True)
        self.scroll.get_overlay_scrolling()
        self.scroll.set_margin_left(self._gtk.action_bar_width * 2)
        self.scroll.set_margin_right(self._gtk.action_bar_width * 2)

        self.scroll.add(gridBox)

        self._screen._fw_config["mcu"]["manual_cfg"] = True
        # get fw_config from screen to know if we are in manual or wizzard config
        validate_button = {
            "text": _("Continue"),
            "panel_link": "co_print_mcu_usb_ids",
            "panel_link_b": "co_print_mcu_clock_reference"
        }

        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}

        if "manual_cfg" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["manual_cfg"] = False

        if self._screen._fw_config["mcu"]["manual_cfg"]:
            validate_button["panel_link"] = "co_print_fwmenu_selection"
            validate_button["panel_link_b"] = "co_print_fwmenu_selection"
            validate_button["text"] = _('Save')

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
        main.pack_end(buttonBox, False, False, 15)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.pack_start(mainBackButtonBox, False, False, 0)
        page.pack_start(main, True, True, 0)

        self.content.add(page)

    def on_click_continue_button(self, continueButton, target_panel):
        if self.selected:
            if "mcu" not in self._screen._fw_config:
                self._screen._fw_config["mcu"] = {}

            self._screen._fw_config["mcu"]["com_interface"] = self.selected
            self._screen.show_panel(target_panel, target_panel, None, 2)

    def on_click_back_button(self, button, target_panel):
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def radioButtonSelected(self, button, com_interface):
        self.selected = com_interface

    def _resolve_radio(self, master_radio):
        active = next((
            radio for radio in
            master_radio.get_group()
            if radio.get_active()
        ))
        return active
