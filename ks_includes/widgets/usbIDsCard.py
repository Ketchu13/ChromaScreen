import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango


class UsbIdCard(Gtk.Box):

    def __init__(self, this, usb_id, callback=None):
        super().__init__()

        self.usb_id = usb_id
        self.parent = this
        self.new_id = self.usb_id["id_default"]
        self.callback = callback

        self.is_active = False
        self.is_sensitive = True


        self.mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, name="usb-id-card-box")

        self.name = "<b>%s:</b>" % (self.usb_id["desc"])

        self.NameLabel = Gtk.Label('', name="usb-id-name-label")
        self.NameLabel.set_justify(Gtk.Justification.LEFT)
        self.NameLabel.set_markup(self.name)
        # set size
        self.NameLabel.set_size_request(100, 20)
        # set max chars
        self.NameLabel.set_max_width_chars(20)
        # align to parent left
        self.NameLabel.set_halign(Gtk.Align.START)
        # align to parent middle
        self.NameLabel.set_valign(Gtk.Align.CENTER)

        self.entry = Gtk.Entry(name="usbid-entry")
        self.entry.set_text(self.usb_id["id"])
        self.entry.set_editable(True)
        # set entry size
        self.entry.set_size_request(50, 20)
        self.entry.set_halign(Gtk.Align.CENTER)
        self.entry.set_valign(Gtk.Align.CENTER)
        self.entry.set_max_width_chars(10)

        # add to   the rigth a button with a check iconnn and no text 20,20 size
        self.check_button = Gtk.Button(_("Save"), name="usbid-check-button")
        self.check_button.set_size_request(20, 20)
        self.check_button.set_halign(Gtk.Align.END)
        self.check_button.set_valign(Gtk.Align.CENTER)
        self.check_button.connect("clicked", self._on_check_button_clicked)

        self.default_button = Gtk.Button(_("Default"), name="usbid-default-button")
        self.default_button.set_size_request(20, 20)
        self.default_button.set_halign(Gtk.Align.END)
        self.default_button.set_valign(Gtk.Align.CENTER)
        self.default_button.set_always_show_image(True)
        self.default_button.connect("clicked", self.set_default)

        self.messageLabel = Gtk.Label('', hexpand=True, name="msg-info-label")
        self.messageLabel.set_justify(Gtk.Justification.CENTER)
        self.messageLabel.set_max_width_chars(200)
        # align to parent left
        self.messageLabel.set_halign(Gtk.Align.CENTER)
        # align to parent middle
        self.messageLabel.set_valign(Gtk.Align.CENTER)

        self.main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        # align namelabel to left
        self.main.pack_start(self.NameLabel, False, False, 0)

        self.main.pack_end(self.default_button, False, False, 0)
        self.main.pack_end(self.check_button, False, False, 0)
        self.main.pack_end(self.entry, False, False, 0)

        # set box size
        self.main.set_size_request(300, 30)

        self.mainBox.pack_start(self.main, False, False, 0)
        self.mainBox.pack_end(self.messageLabel, False, False, 0)

        self.add(self.mainBox)

    def _on_check_button_clicked(self, button):
        if self.check_value():
            self.new_id = self.entry.get_text().strip().lower()
            self.usb_id["id"] = self.new_id
            # msg  info       ok
            self.set_message_info(_("Value is in correct format"))
            return True
        else:
            self.set_message_info(_("Bad value.. Must start with 0x and be hexadecimal"), True)
            return False


    def set_default(self, button=None):
        self.new_id = self.usb_id["id_default"]
        self.entry.set_text(self.new_id)
        self.usb_id["id"] = self.new_id
        self.set_message_info(_("Default value set"))

        # reset error/info message

    def get_value(self):
        return self.new_id

    def set_message_info(self, msg, error=False):
        self.messageLabel.set_text(msg)
        if error:
            self.messageLabel.set_name("msg-error-label")
        else:
            self.messageLabel.set_name("msg-info-label")
        self.messageLabel.show()

    def check_value(self, id_=None):
        if not id_:
            new_id = self.entry.get_text().strip()
        else:
            new_id = id_

        if new_id == "":
            return False
        else:
            new_id = new_id.lower()
            # check value is hexadecimal
            if not all(c in "0123456789abcdefx" for c in new_id):
                return False
            if not new_id.startswith("0x"):
                return False
        return True

    def get_name(self):
        return self.usb_id["type"]

    def __dict__(self):
        return {"name": self.usb_id["type"], "id": self.new_id}

    def get_usb_id(self):
        return self.usb_id
