import contextlib
import json
import logging
import os
from ks_includes.widgets.checkbuttonbox import CheckButtonBox
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintPrintingBrandSelection(*args)


class CoPrintPrintingBrandSelection(ScreenPanel):
    def getPrinters(self):
        printers_brands = []
        if os.path.exists(self.printers_folder) and os.path.isdir(self.printers_folder):
            for brand_folder in os.listdir(self.printers_folder):
                # check if base.json exists
                if os.path.exists(os.path.join(self.printers_folder, brand_folder, "base.json")) :
                    # get json from file
                    with open(os.path.join(self.printers_folder, brand_folder, "base.json")) as json_file:
                        printers_brand = json.load(json_file)
                    # get the printer files to load
                    printers_filename_to_load = printers_brand["printers"]
                    # remove printers from json
                    printers_brand["printers"] = []
                    # for each printer file in the list of printers to load
                    for printer_filename in printers_filename_to_load:
                        # load printer json file
                        printerfile_path = os.path.join(self.printers_folder, brand_folder, "%s.json" % printer_filename)
                        if os.path.exists(printerfile_path) and os.path.isfile(printerfile_path):  # todo check extension
                            with open(printerfile_path, 'r', encoding="utf-8") as json_file:
                                # add printer json to printers_brand
                                printers_brand["printers"].append(json.load(json_file))
                    # avoid empty brands
                    if len(printers_brand["printers"]) > 0:
                        printers_brands.append(printers_brand)
        return printers_brands

    def getPrinterPicture(self, image_path=None, width=None, height=None):
        if image_path is not None:
            if os.path.exists(image_path):
                width = width if width is not None else 50
                height = height if height is not None else 50
                with contextlib.suppress(Exception):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image_path, int(width), int(height))
                    if pixbuf is not None:
                        return pixbuf
        logging.error(f"Unable to find image {image_path}")
        return None

    def __init__(self, screen, title):
        super().__init__(screen, title)
     
        initHeader = InitHeader(self, _('Connect Your 3D Printer'), _('Connect your 3D printer to Co Print Smart using a USB cable.'), "yazicibaglama")
        
        self.image = self._gtk.Image("printer", self._gtk.content_width * .42 , self._gtk.content_height * .42)
        self.printers_folder = os.path.join(os.path.dirname(__file__), "printers")

        self.continueButton = Gtk.Button(_('Finish'),name="flat-button-blue-brand")
        self.continueButton.connect("clicked", self.on_click_continue_button)
        self.continueButton.set_hexpand(True)
        self.continueButton.set_always_show_image (True)
        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonBox.pack_start(self.continueButton, False, False, 0)
        
        backIcon = self._gtk.Image("back-arrow", 35, 35)
        backLabel = Gtk.Label(_("Back"), name="bottom-menu-label")            
        backButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        backButtonBox.set_halign(Gtk.Align.CENTER)
        backButtonBox.set_valign(Gtk.Align.CENTER)
        backButtonBox.pack_start(backIcon, False, False, 0)
        backButtonBox.pack_start(backLabel, False, False, 0)
        self.backButton = Gtk.Button(name="back-button")
        self.backButton.add(backButtonBox)
        self.backButton.connect("clicked", self.on_click_back_button, 'co_print_printing_selection_port')
        self.backButton.set_always_show_image(True)
        mainBackButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mainBackButtonBox.pack_start(self.backButton, False, False, 0)

        self.treestore = Gtk.TreeStore(str, bool)

        self.printer_bands = self.getPrinters()
        for brand in self.printer_bands:
            brand_cat = self.treestore.append(None, [brand["name"], False])
            for printer in brand["printers"]:
                # set parent checked too if is-default is true
                if printer["is-default"]:
                    self.treestore.set_value(brand_cat, 1, True)
                self.treestore.append(brand_cat, [printer["name"], printer["is-default"]])

        self.treeview = Gtk.TreeView(model=self.treestore, name="tree-list")
        self.treeview.set_headers_visible(False)

        renderer_brand_name = Gtk.CellRendererText()
        renderer_brand_name.set_property("font", "Sans Bold 12")

        column_brand_name = Gtk.TreeViewColumn("Brand", renderer_brand_name, text=0)

        self.treeview.append_column(column_brand_name)

        self.treeview.expand_all()
        selection = self.treeview.get_selection()
        selection.connect("changed", self.on_tree_selection_changed)
        self.treeview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.scroll.set_kinetic_scrolling(True)
        self.scroll.get_overlay_scrolling()

        self.scroll.add(self.treeview)

        self.selectedPrinterName = Gtk.Label("Creality Ender 3 Pro", name="selected-printer-name")
        self.selectedPrinterDimension = Gtk.Label(_('Dimension') + ": " + "235mm × 235mm x 300mm", name="selected-printer-dimension")
        self.selectedPrinterBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.selectedPrinterBox.set_name("selected-printer-box")
        self.selectedPrinterBox.pack_start(self.image, False, False, 0)
        self.selectedPrinterBox.pack_start(self.selectedPrinterName, False, False, 10)
        self.selectedPrinterBox.pack_start(self.selectedPrinterDimension, False, False, 0)
        self.selectedPrinterBox.pack_end(buttonBox, False, False, 5)

        pageBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        pageBox.set_name("brand-selection-box")
    
        pageBox.set_halign(Gtk.Align.CENTER)
        pageBox.pack_start(self.scroll, False, False, 0)
        pageBox.pack_start(self.selectedPrinterBox, False, False, 0)
        
        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        main.pack_start(mainBackButtonBox, False, False, 0)
        main.pack_start(initHeader, False, False, 0)
        main.pack_start(pageBox, False, False, 0)
      
        self.content.add(main)

    def on_click_continue_button(self, continueButton):
        self._screen.show_panel("co_print_home_screen", "co_print_home_screen", None, 2)
        
    def on_tree_selection_changed(self, selection):
        # only one item can be selected
        model, iter_ = selection.get_selected()

        if iter_ is not None:
            # if a printer is selected
            if model.iter_parent(iter_) is not None:
                parent_iter = model.iter_parent(iter_)
                parent_name = model[parent_iter][0] if parent_iter is not None else ""

                # change cell background color
                model[iter_][1] = not model[iter_][1]

                # get printer
                printer_selected = {}
                for brand_ in self.printer_bands:
                    if brand_["name"] == parent_name:
                        for printer_ in brand_["printers"]:
                            if printer_["name"] == model[iter_][0]:
                                printer_selected = printer_
                                break
                        break

                if printer_selected:
                    image_path = os.path.join(self.printers_folder, parent_name, printer_selected["picture"])
                    if os.path.exists(image_path):
                        self.image.set_from_pixbuf(
                            self.getPrinterPicture(
                                image_path,
                                self._gtk.content_width * .42, self._gtk.content_height * .42)
                        )
                    else:
                        self.image = self._gtk.Image("printer", self._gtk.content_width * .42, self._gtk.content_height * .42)

                    self.selectedPrinterName.set_text(printer_selected["name"])
                    # update display

                    size = printer_selected["machine"]["size"]
                    self.selectedPrinterDimension.set_text(
                        _('Dimension') + ": " + "%smm × %smm x %smm" % (size["x"], size["y"], size["z"])
                    )

                    print("You selected brand: %s and model: %s" % (parent_name, printer_selected["name"]))
            
    def on_click_back_button(self, button, data):
        self._screen.show_panel(data, data, "Language", 1, False)
