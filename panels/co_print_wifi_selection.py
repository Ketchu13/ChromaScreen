import logging
import os
import re

import gi
import subprocess
from ks_includes.widgets.wificard import WifiCard
from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
import netifaces
from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintWifiSelection(*args)


class CoPrintWifiSelection(ScreenPanel):
    def scan_wifi_networks(self, interface="wlan0"):
        try:
            # Exécute la commande pour scanner les réseaux WiFi
            result = os.popen(f"sudo iw dev {interface} scan").read()

            # Utiliser des expressions régulières pour extraire les informations des réseaux WiFi
            pattern_ssid = re.compile(r"SSID: (.+)")
            pattern_signal_strength = re.compile(r"signal: (.+) dBm")

            # Rechercher les correspondances dans le résultat du scan
            matches_ssid = pattern_ssid.findall(result)
            matches_signal_strength = pattern_signal_strength.findall(result)

            wifi_list = {}
            # update Wi-Fi signal strength by a picture
            for idx, matche_ssid in enumerate(matches_ssid):
                wifi_list[str(idx)] = {"Name": matche_ssid}
                signal_dbm = float(matches_signal_strength[idx])
                wifi_list[str(idx)]["signal_dbm"] = signal_dbm
                print(wifi_list[str(idx)]['Name'])
                if int(signal_dbm) > -50:
                    wifi_list[str(idx)]['Icon'] = 'signal-high'
                elif int(signal_dbm) > -70:
                    wifi_list[str(idx)]['Icon'] = 'signal-medium'
                else:
                    wifi_list[str(idx)]['Icon'] = 'signal-low'
            # Écrire les informations dans un fichier JSON
            return wifi_list

        except Exception as e:
            # Gérer les erreurs liées à l'exécution de la commande
            print(f"Erreur lors de la récupération des réseaux WiFi : {str(e)}")
            return None

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.selectedWifiIndex = None

        self.wifies = []
        # self.wifi_list = self.scan_wifi_networks()

        initHeader = InitHeader(
            self,
            _('Connection Settings'),
            _('Connect the device by entering the information of the network you are using.'),
            "wifi"
        )

        wifi_flowbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        wifi_flowbox.set_halign(Gtk.Align.CENTER)
        wifi_flowbox.set_hexpand(True)

        spinner = Gtk.Spinner()
        spinner.props.width_request = 100
        spinner.props.height_request = 100
        spinner.start()

        GLib.idle_add(self.refresh, None)

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_kinetic_scrolling(True)
        self.scroll.get_overlay_scrolling()
        # self.scroll.set_halign(Gtk.Align.CENTER)
        # self.scroll.set_min_content_width(self._screen.height * .3)
        self.scroll.add(spinner)

        refreshIcon = self._gtk.Image("update", self._screen.width * .028, self._screen.width * .028)
        refreshButton = Gtk.Button(name="setting-button")
        refreshButton.connect("clicked", self.refresh)
        refreshButton.set_image(refreshIcon)
        refreshButton.set_always_show_image(True)
        refreshButtonBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        refreshButtonBox.set_valign(Gtk.Align.CENTER)
        refreshButtonBox.add(refreshButton)

        self.continueButton = Gtk.Button(_('Continue'), name="flat-button-blue")
        self.continueButton.connect("clicked", self.on_click_continue_button)
        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        buttonBox.set_halign(Gtk.Align.CENTER)
        buttonBox.pack_start(self.continueButton, False, False, 0)
        buttonBox.pack_start(refreshButtonBox, False, False, 0)

        backIcon = self._gtk.Image("back-arrow", 35, 35)
        backLabel = Gtk.Label(_("Back"), name="bottom-menu-label")
        backButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        backButtonBox.set_halign(Gtk.Align.CENTER)
        backButtonBox.set_valign(Gtk.Align.CENTER)
        backButtonBox.pack_start(backIcon, False, False, 0)
        backButtonBox.pack_start(backLabel, False, False, 0)

        self.backButton = Gtk.Button(name="back-button")
        self.backButton.add(backButtonBox)
        self.backButton.connect("clicked", self.on_click_back_button, 'co_print_product_naming')
        self.backButton.set_always_show_image(True)

        mainBackButtonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        mainBackButtonBox.pack_start(self.backButton, False, False, 0)

        self.main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main.set_halign(Gtk.Align.CENTER)
        self.main.pack_start(initHeader, False, False, 0)
        self.main.pack_start(self.scroll, False, True, 10)
        self.main.pack_end(buttonBox, False, False, 10)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.pack_start(mainBackButtonBox, False, False, 0)
        page.pack_start(self.main, False, True, 0)

        self.content.add(page)

    def wifiChanged(self, widget, event, name):
        self.selectedWifiIndex = name
        self._screen.show_panel("co_print_wifi_selection_select", "co_print_wifi_selection_select", None, 2, True, items=self.selectedWifiIndex)

    def on_click_continue_button(self, continueButton):
        """if self.selectedWifiIndex is not None:
            self._screen.show_panel("co_print_wifi_selection_select", "co_print_wifi_selection_select", None, 2, True, items=self.selectedWifiIndex)
        else:
            #self._screen.show_panel("co_print_home_screen", "co_print_home_screen", None, 2)"""
        self._screen.show_panel("co_print_fwmenu_selection", "co_print_fwmenu_selection", None, 2)

    #asıl kullanılan metod bu diğer metodu sayfayı görüntülemek için yazdım
    def refresh(self, widget):
        # refresh the Wi-Fi list
        spinner = Gtk.Spinner()
        spinner.props.width_request = 100
        spinner.props.height_request = 100
        spinner.start()
        # clear the scroll
        for child in self.scroll.get_children():
            self.scroll.remove(child)
        # display the spinner
        self.scroll.add(spinner)
        self.content.show_all()

        GLib.idle_add(self.wifi_process)

    def wifi_process(self):
        wifi_flowbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        wifi_flowbox.set_halign(Gtk.Align.CENTER)
        wifi_flowbox.set_hexpand(True)

        wifi_list = self.scan_wifi_networks()

        if wifi_list:
            connected_wifi = self.connected_wifi()
            for wifi in wifi_list:
                if wifi_list[wifi]['Name'] == connected_wifi:
                    wifi_list[wifi]['Status'] = "Connected"
                else:
                    wifi_list[wifi]['Status'] = "Available"
                wifione = WifiCard(self, wifi_list[wifi]['Icon'], wifi_list[wifi]['Name'], wifi_list[wifi]['Status'])
                wifi_flowbox.pack_start(wifione, False, False, 0)
        # debug /show
        else:
            wifione     = WifiCard(self, "signal-high"  , "Co Print 5G"      , "Connected")
            wifitwo     = WifiCard(self, "signal-high"  , "TurkTelekom Wifi" , "Click to connect.")
            wifithree   = WifiCard(self, "signal-medium", "Superonline Wifi" , "Click to connect.")
            wififour    = WifiCard(self, "signal-medium", "Superonline Wifi" , "Click to connect.")
            wififive    = WifiCard(self, "signal-medium", "Superonline Wifi" , "Click to connect.")
            wifisix     = WifiCard(self, "signal-low"   , "Superonline Wifi2", "Click to connect.")
            wifiseven   = WifiCard(self, "signal-low"   , "Superonline Wifi2", "Click to connect.")

            wifi_flowbox.pack_start(wifione  , True, True, 0)
            wifi_flowbox.pack_start(wifitwo  , True, True, 0)
            wifi_flowbox.pack_start(wifithree, True, True, 0)
            wifi_flowbox.pack_start(wififour , True, True, 0)
            wifi_flowbox.pack_start(wififive , True, True, 0)
            wifi_flowbox.pack_start(wifisix  , True, True, 0)
            wifi_flowbox.pack_start(wifiseven, True, True, 0)

        # clear the scroll
        for child in self.scroll.get_children():
            self.scroll.remove(child)

        self.scroll.add(wifi_flowbox)
        self.content.show_all()

    @staticmethod
    def connected_wifi():
        try:
            result = os.popen(f"iwgetid wlan0 -r").read().strip()
            return result
        except Exception as e:
            print(f"Error while getting connected Wi-Fi name: {str(e)}")
            return None


    # def on_click_continue_button(self, continueButton):
    #     self._screen.show_panel("co_print_fwmenu_selection", "co_print_fwmenu_selection", "Language", 1, False)

    def on_click_back_button(self, button, data):
        self._screen.show_panel(data, data, "Language", None, 2)
