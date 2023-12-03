import locale
import gi

from ks_includes.widgets.initheader import InitHeader
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return CoPrintSplashScreenPanel(*args)


class CoPrintSplashScreenPanel(ScreenPanel):

    def __init__(self, screen, title):
        super().__init__(screen, title)

        self.selected = None

        languages = [
            {'Lang':'en' ,'Name': _('English'), 'Icon': 'English', 'Button': Gtk.RadioButton()},
            {'Lang':'fr' ,'Name': _('French') , 'Icon': 'France' , 'Button': Gtk.RadioButton()},
            {'Lang':'ge' ,'Name': _("Deutsch"), 'Icon': 'Germany', 'Button': Gtk.RadioButton()},
            {'Lang':'tr' ,'Name': _("Turkish"), 'Icon': 'Turkey' , 'Button': Gtk.RadioButton()},
            {'Lang':'it' ,'Name': _('Italian'), 'Icon': 'Italy'  , 'Button': Gtk.RadioButton()},
            {'Lang':'sp' ,'Name': _('Spanish'), 'Icon': 'Spain'  , 'Button': Gtk.RadioButton()},
        ]

        group = None

        initHeader = InitHeader(
            self,
            _('Language Settings'),
            _('Please specify the system language'),
            "Geography"
        )

        '''diller'''
        grid = Gtk.Grid(
            column_homogeneous=True,
            column_spacing=10,
            row_spacing=10
        )
        row = 0
        count = 0

        current_lang = self._config.current_lang

        for language in languages:
            languageImage = self._gtk.Image(language['Icon'], self._gtk.content_width * .05, self._gtk.content_height * .05)
            languageName = Gtk.Label(language['Name'], name="language-label")

            language['Button'] = Gtk.RadioButton.new_with_label_from_widget(group, "")
            checked = current_lang == language['Lang']
            if checked:
                if not language['Button'].get_active():
                    language['Button'].set_active(True)
            else:
                language['Button'].set_active(False)

            language['Button'].connect("toggled", self.radioButtonSelected, language['Lang'])

            languageBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)

            f = Gtk.Frame()

            languageBox.pack_start(languageImage, False, True, 5)
            languageBox.pack_end(language['Button'], False, False, 5)
            languageBox.pack_end(languageName, True, True, 5)
            languageBox.set_size_request(50, 50)

            eventBox = Gtk.EventBox()
            eventBox.connect("button-press-event", self.eventBoxLanguage, language['Button'], language['Lang'])
            eventBox.add(languageBox)

            f.add(eventBox)

            grid.attach(f, count, row, 1, 1)
            if group is None:
                group = language['Button']

            count += 1
            if count % 2 == 0:
                count = 0
                row += 1

        gridBox = Gtk.Box()
        gridBox.set_halign(Gtk.Align.CENTER)
        gridBox.add(grid)

        # TODO add an apply bouton, avoid apply on select

        self.continueButton = Gtk.Button(_('Continue'), name="flat-button-blue", hexpand=True)
        self.continueButton.connect("clicked", self.on_click_continue_button, "s3dp_flash_mode_selection")  #"co_print_contract_approval")

        buttonBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        buttonBox.pack_start(self.continueButton, False, False, 0)

        main = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, vexpand=True)
        main.pack_start(initHeader, True, True, 0)
        main.pack_end(buttonBox, True, True, 20)
        main.pack_end(gridBox, True, True, 20)
        main.set_halign(Gtk.Align.CENTER)
        main.set_valign(Gtk.Align.CENTER)

        self.content.add(main)

    def on_click_continue_button(self, continueButton, target_panel):
        self._screen.show_panel(target_panel, target_panel, None, 2)

    def changeLang(self, lang):
        if self._config.current_lang == lang:
            return
        # Apply the language change to KlipperScreen config
        self._screen.change_language(lang)

        lang_map = {
            'en': 'en_US.UTF-8',
            'tr': 'tr_TR.UTF-8',
            'fr': 'fr_FR.UTF-8',
            'ge': 'de_DE.UTF-8',
            'it': 'it_IT.UTF-8',
            'sp': 'es_ES.UTF-8',
        }

        language_map = {
            'en': 'en_US',
            'tr': 'tr_TR',
            'fr': 'fr_FR',
            'ge': 'de_DE',
            'it': 'it_IT',
            'sp': 'es_ES',
        }

        locale_code = lang_map.get(lang, 'en_US.UTF-8')
        locale_code_language = language_map.get(lang, 'en_US')
        current_system_lang = self.get_system_region()
        # only apply if the system language is different from the selected language
        if current_system_lang != locale_code:
            self._screen.show_panel(
                's3dp_language_wait_msg',
                's3dp_language_wait_msg',
                None,
                2,
                data={
                    "locale_code": locale_code,
                    "locale_code_language": locale_code_language
                }
            )

    def radioButtonSelected(self, button, lang):
        print(button)
        if button.get_active():
            print("radiobutton selected event")
            print(button.get_active())
            button.set_active(True)
            GLib.timeout_add(1500, self.changeLang, lang)

    def eventBoxLanguage(self, event, button, radio, lang=None):
        radio.set_active(not radio.get_active())
        self.radioButtonSelected(radio, lang)

    @staticmethod
    def get_system_region():
        region = 'en_US'
        try:
            system_locale = locale.getlocale()
            if system_locale[0]:
                region = system_locale[0]
        except Exception as e:
            print("Error getting system locale: %s" % e)

        return region
