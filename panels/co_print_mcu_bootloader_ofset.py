import logging
import os
from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintMcuBootloaderOfsetSelection(*args)


class CoPrintMcuBootloaderOfsetSelection(ScreenPanel):
     
    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.selected = None

        bootloaders = [
            {'Name': "8KiB bootloader" ,  'Button': Gtk.RadioButton()},
            {'Name': "20KiB bootloader",  'Button': Gtk.RadioButton()},
            {'Name': "28KiB bootloader",  'Button': Gtk.RadioButton()},
            {'Name': "32KiB bootloader",  'Button': Gtk.RadioButton()},
            {'Name': "34KiB bootloader",  'Button': Gtk.RadioButton()},
            {'Name': "64KiB bootloader",  'Button': Gtk.RadioButton()},
            {'Name': "2KiB bootloader\n(HID Bootloader)", 'Button': Gtk.RadioButton()},
            {'Name': "4KiB bootloader", 'Button': Gtk.RadioButton()},
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
            _('Bootloader Offset'),
            _('Select the bootloader offset located on the board you will be controlling.'),
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
        if "bootloader" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["bootloader"] = None

        for bootloader in bootloaders:


            bootloaderName = Gtk.Label(bootloader['Name'], name="wifi-label")
            bootloaderName.set_alignment(0, 0.5)

            bootloader['Button'] = Gtk.RadioButton.new_with_label_from_widget(group, "")
            bootloader['Button'].set_alignment(1, 0.5)
            bootloader['Button'].connect("toggled", self.radioButtonSelected, bootloader['Name'])

            bootloaderBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40, name="chip")

            f = Gtk.Frame(name="chip")

            bootloaderBox.pack_start(bootloaderName, False, True, 10)
            bootloaderBox.pack_end(bootloader['Button'], False, False, 10)

            f.add(bootloaderBox)

            grid.attach(f, count, row, 1, 1)

            if self._screen._fw_config["mcu"]["bootloader"] == bootloader['Name']:
                bootloader['Button'].set_active(True)
                self.selected = bootloader['Name']
                group = bootloader['Button']

            # set group if chip name is the same as the one in fw_config
            if group is None:
                group = bootloader['Button']
                self.seleccted = bootloader['Name']

            count += 1
            if count % 2 == 0:
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
        self.scroll.set_margin_left(self._gtk.action_bar_width *1)
        self.scroll.set_margin_right(self._gtk.action_bar_width*1)
        
        self.scroll.add(gridBox)
        self._screen._fw_config["mcu"]["manual_cfg"] = True
        # get fw_config from screen to know if we are in manual or wizzard config
        validate_button = {
            "text": _("Continue"),
            "panel_link": "co_print_mcu_clock_reference",
            "panel_link_b": "co_print_mcu_model_selection"
        }
        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}

        if "manual_cfg" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["manual_cfg"] = False

        if self._screen._fw_config["mcu"]["manual_cfg"] == True:
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
        # self._screen.base_panel.visible_menu(False)

    def on_click_continue_button(self, continueButton, target_panel):
        if self.selected:
            if "mcu" not in self._screen._fw_config:
                self._screen._fw_config["mcu"] = {}
            self._screen._fw_config["mcu"]["bootloader"] = self.selected
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
