import logging
import os
from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintMcuComInterface(*args)


class CoPrintMcuComInterface(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.selected = None

        chips = [
            {'Name': "USB (on PA11/PA12)"       ,  'Button': Gtk.RadioButton()},
            {'Name': "Serial (on USART1 PA10/PA9)",  'Button': Gtk.RadioButton()},
            {'Name': "Serial (on USART1 PB7/PB6)",  'Button': Gtk.RadioButton()},
            {'Name': "Serial (on USART2 PA3/PA2)", 'Button': Gtk.RadioButton()},
            {'Name': "Serial (on USART2 PD6/PD5)", 'Button': Gtk.RadioButton()},
            {'Name': "Serial (on USART3 PB11/PB10)",  'Button': Gtk.RadioButton()},
            {'Name': "Serial (on USART3 PD9/PD8)",  'Button': Gtk.RadioButton()},
            {'Name': "CAN bus (on PA11/PA12)",  'Button': Gtk.RadioButton()},
            {'Name': "CAN bus (on PA11/PB9)",  'Button': Gtk.RadioButton()},
            {'Name': "CAN bus (on PA11/PB9)", 'Button': Gtk.RadioButton()}
        ]

        self.labels['actions'] = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            vexpand=False,
            halign=Gtk.Align.CENTER,
            homogeneous=True
        )
        self.labels['actions'].set_size_request(self._gtk.content_width, -1)

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

        for chip in chips:



            chipName = Gtk.Label(chip['Name'], name="wifi-label")
            chipName.set_alignment(0, 0.5)

            chip['Button'] = Gtk.RadioButton.new_with_label_from_widget(group, "")
            chip['Button'].set_alignment(1, 0.5)
            chip['Button'].connect("toggled", self.radioButtonSelected, chip['Name'])

            chipBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40, name="chip")

            f = Gtk.Frame(name="chip")

            chipBox.pack_start(chipName, False, True, 10)
            chipBox.pack_end(chip['Button'], False, False, 10)

            f.add(chipBox)

            grid.attach(f, count, row, 1, 1)

            if self._screen._fw_config["mcu"]["com_interface"] == chip['Name']:
                chip['Button'].set_active(True)
                self.selected = chip['Name']
                group = chip['Button']

            # set group if chip name is the same as the one in fw_config
            if group is None:
                group = chip['Button']
                self.selected = chip['Name']

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
        self.scroll.set_margin_left(self._gtk.action_bar_width *2)
        self.scroll.set_margin_right(self._gtk.action_bar_width*2)

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

    def radioButtonSelected(self, button, name):
        self.selected = name

    def _resolve_radio(self, master_radio):
        active = next((
            radio for radio in
            master_radio.get_group()
            if radio.get_active()
        ))
        return active
