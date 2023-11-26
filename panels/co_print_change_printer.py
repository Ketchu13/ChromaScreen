import logging
import os
from ks_includes.widgets.bottommenu import BottomMenu
from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.printerdetail import PrinterDetail

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintChangePrinter(*args)


class CoPrintChangePrinter(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.selected = None

        printers = self._config.get_printers()

        printer_grid = Gtk.Grid()
        printer_grid.set_row_spacing(20)
        printer_grid.set_column_spacing(20)
        left = 0
        top = 0
        for i, printer in enumerate(printers):
            printer_status_style = "printer-status-not-working"

            if printer['data'].state == 'ready':
                printer_status_style = "printer-status-paused"
            elif printer['data'].state == 'printing':
                printer_status_style = "printer-status-continuing"
            name = list(printer)[0]

            printingDetail = PrinterDetail(self, name, "Printer " + str(i + 1), _(printer['data'].state), printer_status_style,
                                           "printer-"+ str(i+1))
            printer_grid.attach(printingDetail, left, top, 1, 1)
            if left == 0:
                left = 1
            else:
                left = 0
                top += 1



        printerBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        printerBox.set_vexpand(True)
        printerBox.set_valign(Gtk.Align.CENTER)
        printerBox.set_halign(Gtk.Align.CENTER)
        printerBox.pack_start(printer_grid, False, False, 0)

        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_kinetic_scrolling(True)
        scroll.get_overlay_scrolling()
        scroll.set_hexpand(True)
        scroll.add(printerBox)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main.pack_start(scroll, True, True, 0)
        main.pack_end(BottomMenu(self, False), False, True, 0)

        self.content.add(main)

    def radioButtonSelected(self, button, printer):
        self.selected = printer

    def on_button_toggled(self, button):

        if button.get_active():
            print("Radio butonu seçildi:", button.get_label())

    def on_click_continue_button(self, continueButton):
        self._screen.show_panel("co_print_printing_selection_port", "co_print_printing_selection_port", None, 2)
