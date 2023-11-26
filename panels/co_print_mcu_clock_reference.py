import json
import logging
import os
import re

import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintMcuClockReference(*args)


class CoPrintMcuClockReference(ScreenPanel):

    def get_mcu_clock_references(self, architecture, mcu_model):
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
        mcu_clock_references_tmp = []
        formated_arch_name = architecture["key"]
        if formated_arch_name in fw_configs["mcus"]:
            current_arch_data = fw_configs["mcus"][formated_arch_name]
            if "models" in current_arch_data:
                mcu_models_tmp = current_arch_data["models"]
                if "clock_reference" in current_arch_data:
                    for clock_reference in current_arch_data["clock_reference"]:
                        current_clock_reference = current_arch_data["clock_reference"][clock_reference]
                        mcu_model_key_name = None
                        if mcu_model["key"] in mcu_models_tmp:
                            mcu_model_key_name = mcu_model["key"]

                        if mcu_model_key_name is not None and mcu_model_key_name in current_clock_reference or "all" in current_clock_reference:
                            mcu_clock_references_tmp.append(clock_reference)
        mcu_clock_references = []
        if mcu_clock_references_tmp is not None:
            for mcu_clock_reference in mcu_clock_references_tmp:
                # format clock reference name
                new_name = mcu_clock_reference.replace("FREQ_", "").replace("Z", "z")
                # add a space between number and letter
                new_name = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", new_name)

                mcu_clock_references.append({'Name': new_name, 'key':mcu_clock_reference, 'Button': Gtk.RadioButton()})
        return mcu_clock_references

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.fw_configs_path = os.path.join(os.path.dirname(__file__), "fwconfig", "fwconfig.json")

        self.selected = None
        self.architecture = None
        self.selected_mcu_model = None
        self.selected_mcu_clock_reference = None
        self.mcu_clock_references = None

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

        self.mcu_clock_references = self.get_mcu_clock_references(self.architecture, self.selected_mcu_model)

        # debug
        if self.mcu_clock_references is None:
            self.mcu_clock_references = [
                {'Name': "8 MHz crystal", 'Button': Gtk.RadioButton()},
                {'Name': "12 MHz crystal", 'Button': Gtk.RadioButton()},
                {'Name': "16 MHz crystal", 'Button': Gtk.RadioButton()},
                {'Name': "20 MHz crystal", 'Button': Gtk.RadioButton()},
                {'Name': "25 MHz crystal", 'Button': Gtk.RadioButton()},
                {'Name': "Internal clock", 'Button': Gtk.RadioButton()},
            ]
        # end debug

        group = None

        initHeader = InitHeader(
            self,
            _('Clock Reference'),
            _('Select the clock reference located on the board you will be controlling.'),
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

        if "clock_reference" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["clock_reference"] = None

        for mcu_clock_reference in self.mcu_clock_references:



            mcu_clock_referenceName = Gtk.Label(mcu_clock_reference['Name'], name="wifi-label")
            mcu_clock_referenceName.set_alignment(0, 0.5)

            # reduce font size if mcu model name is too long
            if len(mcu_clock_reference['Name']) > 30:
                mcu_clock_referenceName.set_size_request(300, -1)
                mcu_clock_referenceName.set_max_width_chars(30)
                mcu_clock_referenceName.set_ellipsize(Pango.EllipsizeMode.END)

            mcu_clock_reference['Button'] = Gtk.RadioButton.new_with_label_from_widget(group, "")
            mcu_clock_reference['Button'].set_alignment(1, 0.5)
            mcu_clock_reference['Button'].connect("toggled", self.radioButtonSelected, mcu_clock_reference)

            mcu_clock_referenceBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40, name="chip")

            f = Gtk.Frame(name="chip")

            mcu_clock_referenceBox.pack_start(mcu_clock_referenceName, False, True, 10)
            mcu_clock_referenceBox.pack_end(mcu_clock_reference['Button'], False, False, 10)

            f.add(mcu_clock_referenceBox)

            grid.attach(f, count, row, 1, 1)
            if self._screen._fw_config["mcu"]["clock_reference"]:
                if self._screen._fw_config["mcu"]["clock_reference"]['Name'] == mcu_clock_reference['Name']:
                    mcu_clock_reference['Button'].set_active(True)
                    self.selected = mcu_clock_reference
                    group = mcu_clock_reference['Button']

            # set group if mcu_clock_reference name is the same as the one in fw_config
            if group is None:
                group = mcu_clock_reference['Button']
                self.selected = mcu_clock_reference

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
        self.scroll.set_margin_left(self._gtk.action_bar_width * 1)
        self.scroll.set_margin_right(self._gtk.action_bar_width * 1)

        self.scroll.add(gridBox)

        self._screen._fw_config["mcu"]["manual_cfg"] = True
        # get fw_config from screen to know if we are in manual or wizzard config

        validate_button = {
            "text": _("Continue"),
            "panel_link": "co_print_mcu_com_interface",
            "panel_link_b": "co_print_mcu_bootloader_ofset"
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

            self._screen._fw_config["mcu"]["clock_reference"] = self.selected
            self._screen.show_panel(target_panel, target_panel, None, 2)

    def on_click_back_button(self, button, target_panel):
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def radioButtonSelected(self, button, mcu_clock_reference):
        self.selected = mcu_clock_reference

    def _resolve_radio(self, master_radio):
        active = next((
            radio for radio in
            master_radio.get_group()
            if radio.get_active()
        ))
        return active
