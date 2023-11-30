import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango


class DeviceCard(Gtk.Box):

    def __init__(self, this, _device, _devlink):
        super().__init__()

        self.name = _device['DEVNAME']

        self.device = _device
        self.devlink = _devlink
        self.parent = this

        self.status = None


        image = self.parent._gtk.Image(
            "approve",
            self.parent._gtk.content_width * .08,
            self.parent._gtk.content_height * .08
        )

        device_devname = "<b>%s</b>" % self.device['DEVNAME']
        device_devlink_path = "<b>%s</b>" % self.devlink

        deviceNameLabel = Gtk.Label('', name="wifi-name-label")
        deviceNameLabel.set_justify(Gtk.Justification.LEFT)
        deviceNameLabel.set_markup(device_devname)
        # reduce font size if mcu model name is too long
        if len(device_devname) > 30:
            deviceNameLabel.set_size_request(200, 200)
            deviceNameLabel.set_max_width_chars(30)
            deviceNameLabel.set_ellipsize(Pango.EllipsizeMode.START)
        deviceNameLabelBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        deviceNameLabelBox.pack_start(deviceNameLabel, False, False, 0)

        deviceDevlinkPathLabel = Gtk.Label("", name="wifi-status-label")
        deviceDevlinkPathLabel.set_markup(device_devlink_path)
        deviceDevlinkPathLabel.set_justify(Gtk.Justification.LEFT)
        if len(device_devlink_path) > 30:
            deviceDevlinkPathLabel.set_size_request(200, 200)
            deviceDevlinkPathLabel.set_max_width_chars(30)
            deviceDevlinkPathLabel.set_ellipsize(Pango.EllipsizeMode.START)
        deviceDevlinkPathLabelBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        deviceDevlinkPathLabelBox.pack_start(deviceDevlinkPathLabel, False, False, 0)

        deviceLabelsBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        deviceLabelsBox.pack_start(deviceNameLabelBox, False, False, 0)
        deviceLabelsBox.pack_start(deviceDevlinkPathLabelBox, False, False, 0)

        deviceCardBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        deviceCardBox.set_name("wifi-card-box")
        deviceCardBox.pack_start(deviceLabelsBox, False, False, 0)
        deviceCardBox.pack_end(image, False, False, 0)

        cartesianTypeEventBox = Gtk.EventBox()
        cartesianTypeEventBox.connect("button-press-event", this.on_click_callback, self.device, self.devlink)
        cartesianTypeEventBox.add(deviceCardBox)

        self.add(cartesianTypeEventBox)
