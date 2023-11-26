import logging
import os
from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintChipSelection(*args)


class CoPrintChipSelection(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.baudrates = []
        self.selected = None

        curr_baudrate = 4800
        for i in range(0, 225):
            self.baudrates.append({'Name': str(curr_baudrate*i), 'key': str(curr_baudrate), 'Button': Gtk.RadioButton()})
        if len(self.baudrates) > 0:
            # sort baudrates by Name
            self.baudrates = sorted(self.baudrates, key=lambda x: int(x['Name']))
        else:
            self.baudrates = [
                {'Name': "9600"  , 'key': '9600'  , 'Button': Gtk.RadioButton()},
                {'Name': "14400" , 'key': "14400" , 'Button': Gtk.RadioButton()},
                {'Name': "19200" , 'key': "19200" , 'Button': Gtk.RadioButton()},
                {'Name': "38400" , 'key': "38400" , 'Button': Gtk.RadioButton()},
                {'Name': "57600" , 'key': "57600" , 'Button': Gtk.RadioButton()},
                {'Name': "115200", 'key': "115200", 'Button': Gtk.RadioButton()},
                {'Name': "128000", 'key': "128000", 'Button': Gtk.RadioButton()},
                {'Name': "256000", 'key': "256000", 'Button': Gtk.RadioButton()},
            ]

        group = None

        initHeader = InitHeader(
            self,
            _('Select Baud Rate'),
            _('Select the Baud Rate to communicate with the processor you will be using.'),
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

        if "baudrate_serial" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["baudrate_serial"] = None

        for baudrate in self.baudrates:

            baudrateName = Gtk.Label(baudrate['Name'], name="wifi-label")
            baudrateName.set_alignment(0, 0.5)

            baudrate['Button'] = Gtk.RadioButton.new_with_label_from_widget(group, "")
            baudrate['Button'].set_alignment(1, 0.5)
            baudrate['Button'].connect("toggled", self.radioButtonSelected, baudrate)

            baudrateBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20, name="chip")

            f = Gtk.Frame(name="chip")

            baudrateBox.pack_start(baudrateName, False, True, 5)
            baudrateBox.pack_end(baudrate['Button'], False, False, 5)

            f.add(baudrateBox)

            grid.attach(f, count, row, 1, 1)

            if self._screen._fw_config["mcu"]["baudrate_serial"]:
                if self._screen._fw_config["mcu"]["baudrate_serial"]['Name'] == baudrate['Name']:
                    baudrate['Button'].set_active(True)
                    self.selected = baudrate
                    group = baudrate['Button']

            # set group if chip name is the same as the one in fw_config
            if group is None:
                group = baudrate['Button']
                self.selected = baudrate

            count += 1
            if count % 2 == 0:
                count = 0
                row += 1

        gridBox = Gtk.FlowBox()
        gridBox.set_halign(Gtk.Align.CENTER)
        gridBox.add(grid)

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_max_content_height(self._screen.height * .3)
        self.scroll.set_kinetic_scrolling(True)
        self.scroll.get_overlay_scrolling()
        self.scroll.set_margin_left(self._gtk.action_bar_width *2.1)
        self.scroll.set_margin_right(self._gtk.action_bar_width*2.1)

        self.scroll.add(gridBox)
        self.scroll.set_size_request(-1, 10)
        self._screen._fw_config["mcu"]["manual_cfg"] = True

        # get fw_config from screen to know if we are in manual or wizzard config
        validate_button = {
            "text": _("Continue"),
            "panel_link": "s3dp_flash_mode_selection"
        }
        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}

        if "manual_cfg" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["manual_cfg"] = False

        if self._screen._fw_config["mcu"]["manual_cfg"]:
            validate_button["panel_link"] = "co_print_fwmenu_selection"
            validate_button["panel_link_b"] = "co_print_mcu_flash_chip"
            validate_button["text"] = _('Save')


        self.selectedWifiName = Gtk.Label("Custom baud rate:", name="wifi-label")
        self.selectedWifiName.set_alignment(0, 0.5)

        self.entry = Gtk.Entry(name="device-name")
        #self.entry.connect("activate", self.rename)
        #self.entry.connect("touch-event", self.give_name)
        # self.entry.connect("focus-in-event", self._screen.show_keyboard)

        eventBox = Gtk.EventBox()
        #eventBox.connect("button-press-event", self.give_name)
        eventBox.add(self.entry)

        self.selectedWifiBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, name='wifi')

        self.selectedWifiBox.pack_start(self.selectedWifiName, True, True, 5)
        self.selectedWifiBox.pack_end(eventBox, True, True, 15)
        self.selectedWifiBox.set_size_request(150, 70)
        self.selectedWifiBox.set_margin_left(self._gtk.action_bar_width * 2.6)
        self.selectedWifiBox.set_margin_right(self._gtk.action_bar_width * 2.6)

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
        main.pack_end(buttonBox, False, False, 10)
        main.pack_end(self.selectedWifiBox, False, False, 10)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.pack_start(mainBackButtonBox, False, False, 0)
        page.pack_start(main, True, True, 0)

        self.content.add(page)
        # self._screen.base_panel.visible_menu(False)

    def on_click_continue_button(self, continueButton, target_panel):
        custom_baudrate = self.entry.get_text()
        go_next = False
        if custom_baudrate and len(custom_baudrate) > 0:
            self.selected = {'Name': custom_baudrate, 'key': custom_baudrate, 'Button': Gtk.RadioButton()}
            go_next = True
        if self.selected:
            if "mcu" not in self._screen._fw_config:
                self._screen._fw_config["mcu"] = {}

            self._screen._fw_config["mcu"]["baudrate_serial"] = self.selected
            go_next = True
        if go_next:
            self._screen.show_panel(target_panel, target_panel, None, 2)

    def on_click_back_button(self, button, target_panel):
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def radioButtonSelected(self, button, baudrate):
        self.selected = baudrate

    def _resolve_radio(self, master_radio):
        active = next((
            radio for radio in
            master_radio.get_group()
            if radio.get_active()
        ))
        return active
