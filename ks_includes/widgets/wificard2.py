import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango


class WifiCard2(Gtk.Box):

    def __init__(self, this, _network):
        super().__init__()
        self.name = _network['Name']
        self.network = _network
        self.parent = this
        self.status = None

        if self.network["connected"] is False:
            self.status = _(self.network["info"])
        else:
            self.status = _("Connected")

        image = self.parent._gtk.Image(self.network["signal_icon"], self.parent._gtk.content_width * .08,
                                                                    self.parent._gtk.content_height * .08)

        display_name = _("Hidden") if self.network['Name'].startswith("\x00") or self.network['Name'].startswith(
            "\\x00") else f"{self.network['Name']}"
        display_status = "<b>%s</b>" % self.status

        if "encryption" in self.network:
            if self.network["encryption"] == "none":
                self.network["encryption"] = _("Open")
            display_status = "%s - %s" % (display_status, self.network["encryption"])
        if "frequency" in self.network:
            self.network["frequency"] = _(self.network["frequency"])
            display_status = "%s - %s" % (display_status, self.network["frequency"])
        if "ipv4" in self.network and self.network["ipv4"] is not None and self.network["ipv4"] != "":
            display_status = "%s - %s" % (display_status, self.network["ipv4"])

        wifiNameLabel = Gtk.Label(display_name, name="wifi-name-label")
        wifiNameLabel.set_justify(Gtk.Justification.LEFT)
        # reduce font size if mcu model name is too long
        if len(display_name) > 30:
            wifiNameLabel.set_size_request(300, -1)
            wifiNameLabel.set_max_width_chars(30)
            wifiNameLabel.set_ellipsize(Pango.EllipsizeMode.END)
        wifiNameLabelBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        wifiNameLabelBox.pack_start(wifiNameLabel, False, False, 0)

        connectStatusLabel = Gtk.Label("", name="wifi-status-label")
        connectStatusLabel.set_markup(display_status)
        connectStatusLabel.set_justify(Gtk.Justification.LEFT)
        connectStatusLabelBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        connectStatusLabelBox.pack_start(connectStatusLabel, False, False, 0)

        wifiLabelBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        wifiLabelBox.pack_start(wifiNameLabelBox, False, False, 0)
        wifiLabelBox.pack_start(connectStatusLabelBox, False, False, 0)

        wifiCardBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        wifiCardBox.set_name("wifi-card-box")
        wifiCardBox.pack_start(wifiLabelBox, False, False, 0)
        wifiCardBox.pack_end(image, False, False, 0)

        cartesianTypeEventBox = Gtk.EventBox()
        cartesianTypeEventBox.connect("button-press-event", this.wifiChanged, self.network)
        cartesianTypeEventBox.add(wifiCardBox)

        self.add(cartesianTypeEventBox)
