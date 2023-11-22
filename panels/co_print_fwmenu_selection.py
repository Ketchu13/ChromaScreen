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

     
    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.selected = None

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
            {'Name': _("Botloader Offset")  , 'key': 'bootloader'       , "panel_link": "co_print_mcu_bootloader_ofset"},
            {'Name': _("Processor Model")   , 'key': 'model'            , "panel_link": "co_print_mcu_model_selection"},
            {'Name': _("Com Interface")     , 'key': 'com_interface'    , "panel_link": "co_print_mcu_com_interface"},
            {'Name': _("Clock Referance")   , 'key': 'clock_reference'  , "panel_link": "co_print_mcu_clock_reference"}
        ]
        self.menu_items = menu_items

        initHeader = InitHeader(self, panel['title'], panel['text'], panel['icon'])

        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}

        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        for menu_item in menu_items:
            menu_item_value = "..."
            menu_item_name = menu_item['Name']

            if (menu_item['key'] in self._screen._fw_config["mcu"] and
                    len(self._screen._fw_config["mcu"][menu_item['key']]) > 1):
                menu_image_name = "approve"
                menu_item_value = self._screen._fw_config["mcu"][menu_item['key']]
            else:
                menu_image_name = "support"

            menu_item_image = self._gtk.Image(
                menu_image_name,
                self._gtk.content_width * .05,
                self._gtk.content_height * .05
            )

            current_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            menu_name_label = Gtk.Label(menu_item_name)
            menu_name_label.set_alignment(0, 0.5)
            menu_name_label.set_width_chars(30)
            current_row.pack_start(menu_name_label, False, False, 0)

            menu_value_label = Gtk.Label(menu_item_value)
            menu_value_label.set_width_chars(20)
            menu_value_label.set_justify(Gtk.Justification.LEFT)
            current_row.pack_start(menu_value_label, False, False, 0)

            current_row.pack_start(menu_item_image, False, False, 0)

            menu_button_edit = Gtk.Button(label="Edit",name="flat-button-blue", hexpand=True)
            menu_button_edit.set_size_request(30, 30)
            menu_button_edit.connect("clicked", self.on_click_menu_item_edit, menu_item['panel_link'])

            current_row.pack_start(menu_button_edit, False, False, 0)
            current_row.get_style_context().add_class("fw-menu-treeview-row")
            self.mainBox.pack_start(current_row, False, False, 0)


        
        self.checkButton = CheckButtonBox(self, _('Enable extra low-level configuration options'))

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



    def button_data_func(self, column,cell, model, iter, data=None):
        cell.set_property('text', 'Edit')
        cell.set_property('editable', True)
        cell.connect('edited', self.on_cell_edited, model, iter)

    def on_cell_edited(self, cell, path, new_text, model, iter):
        print("cell edited: %s %s %s %s" % (cell, path, new_text, model))

    def on_click_menu_item_edit(self, button, target_panel):
        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}
        self._screen._fw_config["mcu"]["manual_cfg"] = True
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def on_click_continue_button(self, continueButton, target_panel):
        # TODO check mcu dict and go next
        if self.checkButton.get_active():
            self._screen._fw_config["mcu"]["enable_extra"] = True
        else:
            self._screen._fw_config["mcu"]["enable_extra"] = False

    def on_click_wizzard_button(self, continueButton):
        if "mcu" not in self._screen._fw_config:
            self._screen._fw_config["mcu"] = {}
        self._screen.show_panel("co_print_mcu_selection", "co_print_mcu_selection", None, 2)

    def on_click_back_button(self, button, target_panel):
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def on_box_click(self, widget, event):
        self.selected = event
        path_info = self.treeview.get_path_at_pos(event.get_coords()[0],event.get_coords()[1])
        if path_info:
            path, column, x, y = path_info
            model = self.treeview.get_model()
            iter = model.get_iter(path)
            name = model.get_value(iter, 0)
            #get  panel link by name
            panel_link = None
            for menu_item in self.menu_items:
                if menu_item['Name'] == name:
                    panel_link = menu_item['panel_link']
                    break
            if panel_link:
                self._screen.show_panel(panel_link, panel_link, None, 2)

    def _resolve_radio(self, master_radio):
        active = next((
            radio for radio in
            master_radio.get_group()
            if radio.get_active()
        ))
        return active

