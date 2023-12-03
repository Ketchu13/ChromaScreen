import os

import gi

from ks_includes.widgets.initheader import InitHeader

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return S3DPLangWaitMsg(*args)


class S3DPLangWaitMsg(ScreenPanel):
    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.initialized = False

        spinner = Gtk.Spinner()
        spinner.props.width_request = 50
        spinner.props.height_request = 50
        spinner.start()

        msglabel = Gtk.Label(_("Loading selected language.\nPlease wait.."))

        image = self._gtk.Image("Geography", self._gtk.content_width * .3, self._gtk.content_height * .3)
        image.set_halign(Gtk.Align.CENTER)
        image.set_valign(Gtk.Align.CENTER)

        initHeader = InitHeader(
            self,
            _('Language Settings'),
            _("Loading selected language.\nPlease wait.."),
            "Geography"
        )
        msgBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        msgBox.set_halign(Gtk.Align.CENTER)
        msgBox.set_valign(Gtk.Align.CENTER)
        msgBox.set_hexpand(True)
        msgBox.set_vexpand(True)

        msgBox.pack_start(image, True, True, 0)
        msgBox.pack_start(msglabel, True, True, 0)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, vexpand=True)
        main.pack_start(initHeader, True, True, 0)
        main.pack_start(spinner, True, True, 0)
        main.set_halign(Gtk.Align.CENTER)
        main.set_valign(Gtk.Align.CENTER)

        self.content.add(main)
        GLib.idle_add(self.apply_locale)

    def apply_locale(self):
        if not self.initialized:
            return None
        print("data:  ", self.data)
        if self.data is None or "locale_code" not in self.data or \
                "locale_code_language" not in self.data:
            self._screen.show_panel(
                'co_print_splash_screen',
                'co_print_splash_screen',
                None,
                2
            )
            return

        locale_code = self.data["locale_code"]
        locale_code_language = self.data["locale_code_language"]

        sudoPassword = 'c317tek'
        command = 'locale-gen ' + locale_code_language
        p = os.system('echo %s|sudo -S %s' % (sudoPassword, command))

        command2 = 'update-locale LANG=' + locale_code
        p = os.system('echo %s|sudo -S %s' % (sudoPassword, command2))

        command3 = 'update-locale LC_ALL=' + locale_code
        p = os.system('echo %s|sudo -S %s' % (sudoPassword, command3))

    def initialize(self, data=None):
        self.data = data
        self.initialized = True
