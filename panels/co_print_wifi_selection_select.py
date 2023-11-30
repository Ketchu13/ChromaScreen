import logging
import os
import subprocess
import time

import gi
from ks_includes.widgets.infodialog import InfoDialog

from ks_includes.widgets.initheader import InitHeader
from ks_includes.widgets.keyboard import Keyboard
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GLib, Gdk, GdkPixbuf

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintWifiSelectionSelect(*args)


class CoPrintWifiSelectionSelect(ScreenPanel):
    # can also be one

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.prev_network = None
        self.wifi = None
        self.waitDialog = None
        self.password = None
        self.dialog = None
        self.source = None
        self.selectedNetwork = None
        initHeader = InitHeader(
            self,
            _('Connection Settings'),
            _('Connect the device by entering the information of the network you are using.'),
            "wifi"
        )

        # ComboBox'a öğeler ekle
        self.selectedWifiImage = self._gtk.Image("sinyal", self._gtk.content_width * .05, self._gtk.content_height * .05)
        self.selectedWifiName = Gtk.Label("", name="wifi-label")
        self.selectedWifiName.set_alignment(0, 0.5)
        self.selectedWifiImage.set_alignment(1, 0.5)

        self.entry = Gtk.Entry(name="device-name")
        self.entry.connect("activate", self.add_new_network)
        self.entry.connect("touch-event", self.give_name)
        #self.entry.connect("focus-in-event", self._screen.show_keyboard)

        eventBox = Gtk.EventBox()
        eventBox.connect("button-press-event", self.give_name)
        eventBox.add(self.entry)

        self.selectedWifiBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, name='wifi')

        self.selectedWifiBox.pack_start(self.selectedWifiName, True, True, 5)
        self.selectedWifiBox.pack_end(self.selectedWifiImage , True, True, 15)
        self.selectedWifiBox.pack_end(eventBox, True, True, 15)
        self.selectedWifiBox.set_size_request(300, 70)
        self.selectedWifiBox.set_margin_left(self._gtk.action_bar_width  * 2.6)
        self.selectedWifiBox.set_margin_right(self._gtk.action_bar_width * 2.6)

        # add a label to show connection status and progresss
        self.label_connecting_info = Gtk.Label("", name="contract-approval-label")
        self.label_connecting_info.set_halign(Gtk.Align.START)
        self.label_connecting_info.set_valign(Gtk.Align.START)
        self.label_connecting_info.set_line_wrap(True)
        self.label_connecting_info.set_max_width_chars(100)

        self.scroll = self._gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_min_content_height(self._screen.height * .3)
        self.scroll.set_kinetic_scrolling(True)
        self.scroll.get_overlay_scrolling()
        self.scroll.set_margin_left(self._gtk.action_bar_width * 1)
        self.scroll.set_margin_right(self._gtk.action_bar_width * 1)

        self.scroll.add(self.label_connecting_info)

        self.backButton = Gtk.Button(_('Back'), name="flat-button-blue")
        self.backButton.connect("clicked", self.on_click_back_button)

        self.continueButton = Gtk.Button(_('Connect'), name="flat-button-blue")
        self.continueButton.connect("clicked", self.on_click_continue_button)

        self.buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.buttonBox.set_halign(Gtk.Align.CENTER)
        self.buttonBox.pack_start(self.continueButton, False, False, 0)
        self.buttonBox.pack_start(self.backButton, False, False, 0)

        self.tempBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.tempBox.pack_start(self.buttonBox, False, False, 0)

        self.main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.main.pack_start(initHeader, False, False, 0)
        self.main.pack_end(self.tempBox, False, True, 10)
        self.main.pack_end(self.scroll, True, True, 10)
        self.main.pack_end(self.selectedWifiBox, False, True, 10)

        self.content.add(self.main)

    def initialize(self, _network, _wifi):
        self.selectedNetwork = _network
        self.wifi = _wifi
        self.selectedWifiName.set_label(self.selectedNetwork["Name"])
        self.selectedWifiImage = self._gtk.Image(
            self.selectedNetwork["signal_icon"],
            self._gtk.content_width * .08,
            self._gtk.content_height * .08
        )

    def give_name(self,a,b):
        for child in self.tempBox.get_children():
            self.tempBox.remove(child)
        self._screen.show_keyboard()
        self.content.show_all()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_size_request(self._screen.gtk.content_width, self._screen.gtk.keyboard_height)

        box.get_style_context().add_class("keyboard_box")
        box.add(Keyboard(self._screen, self.remove_keyboard, entry=self.entry))
        self.tempBox.pack_end(box, False, False, 0)
        self.content.show_all()

    def remove_keyboard(self, widget=None, event=None):
        for child in self.tempBox.get_children():
            self.tempBox.remove(child)

        self.tempBox.pack_start(self.buttonBox, False, False, 0)
        self.content.show_all()

    def add_new_network(self, widget, event=None):
        print("add new network")
        self._screen.remove_keyboard()
        psk = self.entry.get_text()
        result = False
        if len(psk) < 8:
            self._screen.show_popup_message("Password must be at least 8 characters long")
            return
        # check if network already exists in supplicant
        snets = self.wifi.get_supplicant_networks()
        for netid, net in snets.items():
            if net['ssid'] == self.selectedNetwork["Name"]:
                result = True
                # .wifi.delete_network(netid)
                break
            # add network again
        if not result and len(psk)<=0:
            result = self.wifi.add_network(self.selectedNetwork["Name"], psk)
        elif result and len(psk)<=0:
            result = self.wifi.modify_network(self.selectedNetwork["Name"], psk)
        elif not result and (not psk or len(psk)<8):
            self._screen.show_popup_message("For non known networks, you have to enter a password\nPassword must be at least 8 characters long")
            return

        if result:
            print("SSID: %s - PSK: %s" % (self.selectedNetwork["Name"], psk))
            print("result: ", result)
            self.connect_network(widget, self.selectedNetwork["Name"])
        else:
            self._screen.show_popup_message("Error adding network %s" % self.selectedNetwork["Name"])

    def connect_network(self, widget, ssid):

        snets = self.wifi.get_supplicant_networks()
        isdef = False
        for netid, net in snets.items():
            if net['ssid'] == ssid:
                isdef = True
                break
        # if current network is not defined in supplicant
        if not isdef:
            self.showMessageBox(_('Connection failed.'))
            return

        # msg during connect attempt
        self.prev_network = self.wifi.get_connected_ssid()

        self.label_connecting_info.set_text(_("Starting WiFi Association"))
        self.label_connecting_info.show_all()
        self.wifi.add_callback("connecting_status", self.connecting_status_callback)
        self.wifi.connect(ssid)

    # connection progress terminal output
    def connecting_status_callback(self, msg):
        self.label_connecting_info.set_text(f"{self.label_connecting_info.get_text()}\n{msg}")
        self.label_connecting_info.show_all()

    def connected_callback(self, ssid, prev_ssid):
        logging.info("Now connected to a new network")
        if ssid is not None:
            print("new ssid:", ssid)
        else:
            print("new ssid is None")
            ssid = self.wifi.get_connected_ssid() or "UKN"
        if prev_ssid is not None:
            print("old ssid: ", prev_ssid)
        self.connecting_status_callback(_("Connected to %s") % ssid)
        self.wifi.remove_callback("connecting_status", self.connecting_status_callback)
        self.wifi.remove_callback("connected", self.connected_callback)
        time.sleep(3)
        self.on_click_back_button(None)

    def on_click_back_button(self, button):
        self._screen.show_panel("network", "network", None, 2)

    def execute_command_and_show_output(self):
        try:
            status = self.connect_to(self.selectedNetwork, self.password)

            if status:
                self.close_dialog(self.waitDialog)
                self._screen.show_panel("co_print_wifi_selection_connect", "co_print_wifi_selection_connect", None, 2, True, items=self.selectedNetwork, password=self.password)
            else:
                self.close_dialog(self.waitDialog)
                self.showMessageBox(_('Connection failed.'))

        except subprocess.CalledProcessError as e:
            self.showMessageBox(e.output.decode("utf-8"))

    def close_dialog(self, dialog):
        dialog.response(Gtk.ResponseType.CANCEL)
        dialog.destroy()

    def showMessageBox(self, message):
        self.dialog = InfoDialog(self, message, True)
        self.dialog.get_style_context().add_class("alert-info-dialog")

        self.dialog.set_decorated(False)
        self.dialog.set_size_request(0, 0)
        timer_duration = 3000
        GLib.timeout_add(timer_duration, self.close_dialog, self.dialog)
        response = self.dialog.run()

    def on_click_continue_button(self, continueButton):
        self.add_new_network(None)

    def what_wifi(self):
        process = subprocess.run(['nmcli', '-t', '-f', 'ACTIVE,SSID', 'dev', 'wifi'], stdout=subprocess.PIPE)
        if process.returncode == 0:
            return process.stdout.decode('utf-8').strip()
        else:
            return ''

    def is_connected_to(self, ssid: str):
        return 'yes:' + ssid in self.what_wifi()

    def scan_wifi(self):
        process = subprocess.run(['nmcli', '-t', '-f', 'SSID,SECURITY,SIGNAL', 'dev', 'wifi'], stdout=subprocess.PIPE)
        if process.returncode == 0:
            return process.stdout.decode('utf-8').strip().split('\n')
        else:
            return []

    def is_wifi_available(self, ssid: str):
        return ssid in [x.split(':')[0] for x in self.scan_wifi()]

    def connect_to(self, ssid: str, password: str):
        subprocess.call(['nmcli', 'd', 'wifi', 'connect', ssid, 'password', password])
        return self.is_connected_to(ssid)

    def connect_to_saved(self, ssid: str):
        if not self.is_wifi_available(ssid):
            return False
        subprocess.call(['nmcli', 'c', 'up', ssid])
        return self.is_connected_to(ssid)
