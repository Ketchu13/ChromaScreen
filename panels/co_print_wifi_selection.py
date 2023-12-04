import logging
import os

import gi
import netifaces

from ks_includes.widgets.initheader import InitHeader
from ks_includes.widgets.wificard2 import WifiCard2

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib
from ks_includes.screen_panel import ScreenPanel

# TODO add message / display to notify that no wireless interface found
def create_panel(*args):
    return CoPrintWifiSelection(*args)


class CoPrintWifiSelection(ScreenPanel):
    initialized = False

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.selectedWifiIndex = None
        self.show_add = False

        self.networks = {}

        self.interface = None
        self.prev_network = None

        self.update_timeout = None

        self.network_interfaces = netifaces.interfaces()
        self.wireless_interfaces = [iface for iface in self.network_interfaces if iface.startswith('w')]

        self.wifi = None
        self.ip = None
        self.use_network_manager = os.system('systemctl is-active --quiet NetworkManager.service') == 0

        if len(self.wireless_interfaces) > 0:
            logging.info(f"Found wireless interfaces: {self.wireless_interfaces}")
            if self.use_network_manager:
                logging.info("Using NetworkManager")
                from ks_includes.wifi_nm import WifiManager
            else:
                logging.info("Using wpa_cli")
                from ks_includes.wifi import WifiManager
            self.wifi = WifiManager(self.wireless_interfaces[0])


            # Get interface
            gws = netifaces.gateways()
            if "default" in gws and netifaces.AF_INET in gws["default"]:
                self.interface = gws["default"][netifaces.AF_INET][1]
            else:
                ints = netifaces.interfaces()
                if 'lo' in ints:
                    ints.pop(ints.index('lo'))
                if len(ints) > 0:
                    self.interface = ints[0]
                else:
                    self.interface = 'lo'
            # Get IP Address
            res = netifaces.ifaddresses(self.interface)
            if netifaces.AF_INET in res and len(res[netifaces.AF_INET]) > 0:
                self.ip = res[netifaces.AF_INET][0]['addr']
            else:
                self.ip = None
        else:
            # ChromaPad don't have any ethernet port, so we don't need to show ethernet networks
            # and if no wireless interfaces found, I'm afraid Dave, we have to use loopback interface
            logging.error("No wireless interfaces found")
            # display msg
            # for now just return

        # template try 1
        initHeader = InitHeader(
            self,
            _('Connection Settings'),
            _('Connect the device by entering the information of the network you are using.'),
            "wifi"
        )

        spinner = Gtk.Spinner()
        spinner.props.width_request = 100
        spinner.props.height_request = 100
        spinner.start()

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_kinetic_scrolling(True)
        self.scroll.get_overlay_scrolling()
        # self.scroll.set_halign(Gtk.Align.CENTER)
        # self.scroll.set_min_content_width(self._screen.height * .3)
        self.scroll.add(spinner)

        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        buttonBox.set_halign(Gtk.Align.CENTER)

        self.continueButton = Gtk.Button(_('Continue'), name="flat-button-blue")
        self.continueButton.connect("clicked", self.on_click_continue_button)
        self.continueButton.set_sensitive(False)
        buttonBox.pack_start(self.continueButton, False, False, 0)

        self.ip_label = Gtk.Label()
        self.ip_label.set_hexpand(True)
        buttonBox.pack_start(self.ip_label, False, False, 0)

        if self.ip is not None:
            self.update_ip_label(ip=self.ip)

        refreshIcon = self._gtk.Image("update", self._screen.width * .028, self._screen.width * .028)
        refreshButton = Gtk.Button(name="setting-button")
        refreshButton.connect("clicked", self.reload_networks)
        refreshButton.set_image(refreshIcon)
        refreshButton.set_always_show_image(True)
        refreshButtonBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        refreshButtonBox.set_valign(Gtk.Align.CENTER)
        refreshButtonBox.add(refreshButton)
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
        self.content.show_all()

        # self.wifi.add_callback("connected", self.connected_callback)
        # self.wifi.add_callback("scan_results", self.scan_callback)
        if self.wifi:
            self.wifi.add_callback("popup", self.popup_callback)

        if self.update_timeout is None:
            self.update_timeout = GLib.timeout_add_seconds(5, self.reload_networks)

        self.initialized = True

    def update_ip_label(self, ip):
        self.ip_label.set_text(f"IP: {ip}  ")
        self.continueButton.set_sensitive(True)

    @staticmethod
    def get_signal_icon(signal_dbm):
        icon = 'signal-none'
        try:
            signal_dbm = float(signal_dbm)
            if int(signal_dbm) > -50:
                icon = 'signal-high'
            elif int(signal_dbm) > -70:
                icon = 'signal-medium'
            else:
                icon = 'signal-low'
        except Exception as e:
            logging.error(f"Error getting signal icon: {e}")
        return icon

    def wifiChanged(self, widget, event, _network):
        self.selectedWifiIndex = _network
        if "Name" in _network:
            if self.update_timeout is not None:
                GLib.source_remove(self.update_timeout)
                self.update_timeout = None
            self._screen.show_panel("co_print_wifi_selection_select", "co_print_wifi_selection_select", None, 2, True,
                                    _network=self.selectedWifiIndex, _wifi=self.wifi)

    def wifi_process(self):
        self.networks = self.wifi.get_networks()
        if not self.networks:
            return

        wifi_flowbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, halign=Gtk.Align.CENTER)
        wifi_flowbox.set_hexpand(True)

        for network in self.networks:
            curr_network = {'Name': network}
            netinfo = self.wifi.get_network_info(network)
            if "connected" in netinfo:
                curr_network["connected"] = netinfo['connected']
            else:
                curr_network["connected"] = False
            if curr_network["connected"] or self.wifi.get_connected_ssid() == network:
                stream = os.popen('hostname -f')
                hostname = stream.read().strip()
                ifadd = netifaces.ifaddresses(self.interface)
                if netifaces.AF_INET in ifadd and len(ifadd[netifaces.AF_INET]) > 0:
                    self.ip = ifadd[netifaces.AF_INET][0]['addr']
                    curr_network["ipv4"] = f"<b>IPv4:</b> {self.ip} "
                    self.ip_label.set_text(self.ip)
                else:
                    curr_network["ipv4"] = ""
                if netifaces.AF_INET6 in ifadd and len(ifadd[netifaces.AF_INET6]) > 0:
                    curr_network["ipv6"] = f"<b>IPv6:</b> {ifadd[netifaces.AF_INET6][0]['addr'].split('%')[0]} "
                else:
                    curr_network["ipv6"] = ""
                curr_network["info"] = '<b>' + _(
                    "Hostname") + f':</b> {hostname}\n{curr_network["ipv4"]}\n{curr_network["ipv6"]}\n'
            elif "psk" in netinfo:
                curr_network["info"] = _("Password saved")
            else:
                curr_network["info"] = _("Available")
            if "encryption" in netinfo:
                if netinfo['encryption'] != "off":
                    curr_network["encryption"] = netinfo['encryption'].upper()
            if "frequency" in netinfo:
                curr_network["frequency"] = "2.4 GHz" if netinfo['frequency'][0:1] == "2" else "5 Ghz"
            if "channel" in netinfo:
                curr_network["channel"] = _("Channel") + f' {netinfo["channel"]}'
            if "signal_level_dBm" in netinfo:
                curr_network["signal_level_dBm"] = f'{netinfo["signal_level_dBm"]} ' + _("dBm")
                curr_network["signal_icon"] = self.get_signal_icon(netinfo["signal_level_dBm"])
            # check item validity
            if ("signal_icon" not in curr_network or
                    "Name" not in curr_network or
                    "connected" not in curr_network or
                    (curr_network["connected"] is False and "info" not in curr_network)):
                print("invalid network:", curr_network)
                continue

            wifi_card = WifiCard2(
                self,
                curr_network
            )
            wifi_flowbox.pack_start(wifi_card, False, False, 0)

        # clear the scroll
        for child in self.scroll.get_children():
            self.scroll.remove(child)

        self.scroll.add(wifi_flowbox)
        self.content.show_all()

    def popup_callback(self, msg):
        print("popup_callback:", msg)
        self._screen.show_popup_message(msg)

    def connected_callback(self, ssid, prev_ssid):
        print("Now connected to a new network")
        self.reload_networks()

    def get_connected_network_info(self):
        stream = os.popen('hostname -f')
        hostname = stream.read().strip()
        ifadd = netifaces.ifaddresses(self.interface)
        ipv4 = ""
        ipv6 = ""
        if netifaces.AF_INET in ifadd and len(ifadd[netifaces.AF_INET]) > 0:
            ipv4 = ifadd[netifaces.AF_INET][0]['addr']
            # self.labels['ip'].set_text(f"IP: {ifadd[netifaces.AF_INET][0]['addr']}  ")
        if netifaces.AF_INET6 in ifadd and len(ifadd[netifaces.AF_INET6]) > 0:
            ipv6 = ifadd[netifaces.AF_INET6][0]['addr'].split('%')[0]

        network_infos = {
            "hostname": hostname,
            "ipv4": ipv4,
            "ipv6": ipv6,
            "interface": self.interface,
            "connected": True
        }
        return network_infos

    def reload_networks(self, widget=None):
        if self.wifi and self.wifi.initialized:
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

    def on_click_continue_button(self, continueButton, target_panel=None):
        logging.info("on_click_continue_button")
        self._screen.show_panel("co_print_fwmenu_selection", "co_print_fwmenu_selection", None, 2)

    def on_click_back_button(self, button, target_panel=None):
        self._screen.show_panel("co_print_product_naming", "co_print_product_naming", None, 2)
