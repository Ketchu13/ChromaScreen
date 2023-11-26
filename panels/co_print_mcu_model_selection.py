import json
import logging
import os
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintMcuModelSelection(*args)


class CoPrintMcuModelSelection(ScreenPanel):

    def get_mcu_models(self, architecture):
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
        mcu_models_tmp = None
        formated_arch_name = architecture["key"]
        if formated_arch_name in fw_configs["mcus"]:
            current_arch_data = fw_configs["mcus"][formated_arch_name]
            if "models" in current_arch_data:
                mcu_models_tmp = current_arch_data["models"]
        mcu_models = []
        if mcu_models_tmp is not None:
            for mcu_model in mcu_models_tmp:
                mcu_models.append(
                    {
                        'Name': mcu_models_tmp[mcu_model]["name"],
                        'key': mcu_model,
                        'Button': Gtk.RadioButton()
                    }
                )
        return mcu_models

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.fw_configs_path = os.path.join(os.path.dirname(__file__), "fwconfig", "fwconfig.json")

        self.selected = None

        self.architecture = None

        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}

        if "architecture" in self._screen._fw_config["mcu"]:
            # get mcu models for the selected architecture from ./fwconfig.json
            self.architecture = self._screen._fw_config["mcu"]["architecture"]

        if self.architecture is None:
            # return to previous panel if architecture is not selected
            self._screen.show_panel("co_print_mcu_selection", "co_print_mcu_selection", None, 2)
            return

        # get mcu models for the selected architecture from ./fwconfig.json
        self.mcu_models = self.get_mcu_models(self.architecture)
        # debug
        if self.mcu_models is None:
            self.mcu_models = [
                {'Name': "STM32F103", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F207", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F401", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F405", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F407", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F429", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F446", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F031", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F042", 'Button': Gtk.RadioButton()},
                {'Name': "STM32F070", 'Button': Gtk.RadioButton()},
            ]
        # end debug

        group = None
        # TODO replace chip by processor model
        initHeader = InitHeader(
            self,
            _('Select the Chip Model'),
            _('Select the MCU model located on the board you will be controlling.'),
            "mikrochip"
        )

        '''diller'''
        grid = Gtk.Grid(
            column_homogeneous=True,
            column_spacing=10,
            row_spacing=10
        )
        row = 0
        count = 0

        if "model" not in self._screen._fw_config["mcu"]:
            self._screen._fw_config["mcu"]["model"] = None

        for mcu_model in self.mcu_models:
            mcu_modelImage = None

            mcu_modelName = Gtk.Label(mcu_model['Name'], name="wifi-label")
            mcu_modelName.set_alignment(0, 0.5)
            # reduce font size if mcu model name is too long
            if len(mcu_model['Name']) > 30:
                mcu_modelName.set_size_request(300, -1)
                mcu_modelName.set_max_width_chars(30)
                mcu_modelName.set_ellipsize(Pango.EllipsizeMode.END)

            mcu_model['Button'] = Gtk.RadioButton.new_with_label_from_widget(group, "")
            mcu_model['Button'].set_alignment(1, 0.5)
            mcu_model['Button'].connect("toggled", self.radioButtonSelected, mcu_model)

            mcu_modelBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40, name="chip")

            f = Gtk.Frame(name="chip")

            mcu_modelBox.pack_start(mcu_modelName, False, True, 10)
            mcu_modelBox.pack_end(mcu_model['Button'], False, False, 10)

            f.add(mcu_modelBox)

            grid.attach(f, count, row, 1, 1)

            if self._screen._fw_config["mcu"]["model"]:
                if self._screen._fw_config["mcu"]["model"]['Name'] == mcu_model['Name']:
                    mcu_model['Button'].set_active(True)
                    self.selected = mcu_model
                    group = mcu_model['Button']

            # set group if chip name is the same as the one in fw_config
            if group is None:
                group = mcu_model['Button']
                self.selected = mcu_model

            # only 1 col for avoids to have to cut the text
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
        self.scroll.set_margin_left(self._gtk.action_bar_width * 1)
        self.scroll.set_margin_right(self._gtk.action_bar_width * 1)

        self.scroll.add(gridBox)
        self._screen._fw_config["mcu"]["manual_cfg"] = True
        # get fw_config from screen to know if we are in manual or wizzard config
        validate_button = {
            "text": _("Continue"),
            "panel_link": "co_print_mcu_bootloader_ofset",
            "panel_link_b": "co_print_mcu_selection"
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
        # self._screen.base_panel.visible_menu(False)

    def on_click_continue_button(self, continueButton, target_panel):
        if self.selected:
            if "mcu" not in self._screen._fw_config:
                self._screen._fw_config["mcu"] = {}

            # save to fw_config
            self._screen._fw_config["mcu"]["model"] = self.selected
            # open target panel
            self._screen.show_panel(target_panel, target_panel, None, 2)

    def on_click_back_button(self, button, target_panel):
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def radioButtonSelected(self, button, mcu_model):
        self.selected = mcu_model

    def _resolve_radio(self, master_radio):
        active = next((
            radio for radio in
            master_radio.get_group()
            if radio.get_active()
        ))
        return active
