# window.py
#
# Copyright 2018 Jordan Petridis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, Gio, GObject
from .gi_composites import GtkTemplate


@GtkTemplate(ui='/org/gnome/Kasbah/window.ui')
class KasbahWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'KasbahWindow'

    capture_stack = GtkTemplate.Child()
    menu = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        capture = CaptureBox()
        save = SaveBox()

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        self.capture_stack.add_named(capture, "capture")
        self.capture_stack.add_named(save, "save")

        self.menu.props.menu_model = self.props.application. \
            get_menu_by_id('win-menu')
        self.show_all()

    def on_about(self, act, p):
        artists = ['Tobias Bernard']
        authors = ['Jordan Petridis', 'Zander Brown']
        # TODO: Translatable
        comments = 'Save images of your screen or individual windows'
        website = 'https://gitlab.gnome.org/alatiera/Kasbah'
        about_dialog = Gtk.AboutDialog(transient_for=self,
                                       modal=True,
                                       artists=artists,
                                       authors=authors,
                                       comments=comments,
                                       copyright='© 2018 Jordan Petridis',
                                       license_type=Gtk.License.AGPL_3_0,
                                       logo_icon_name='org.gnome.Kasbah',
                                       program_name='Kasbah',
                                       version='0.0.1',
                                       website=website,
                                       website_label='Repository')
        about_dialog.present()


@GtkTemplate(ui='/org/gnome/Kasbah/capture.ui')
class CaptureBox(Gtk.Box):
    __gtype_name__ = 'CaptureBox'
    _mode = 'Window'
    _toggle_flag = False

    # The 3 radio buttons
    screen = GtkTemplate.Child()
    window = GtkTemplate.Child()
    selection = GtkTemplate.Child()

    # The usefull switches from the widget
    # We will need to map actions to them later
    pointer = GtkTemplate.Child()
    shadow = GtkTemplate.Child()
    delay = GtkTemplate.Child()

    # Options list
    listbox = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        settings = Gio.Settings.new('org.gnome.Kasbah')
        flags = Gio.SettingsBindFlags.DEFAULT
        settings.bind('include-pointer', self.pointer, 'active', flags)
        settings.bind('window-shadow', self.shadow, 'active', flags)
        settings.bind('delay', self.delay, 'value', flags)
        settings.bind('mode', self, 'mode', flags)

        self.listbox.set_header_func(self.update_header)

    @GObject.Property(type=str, nick='Screenshot mode')
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
        print(value)
        if value == 'Selection':
            if not self._toggle_flag:
                self.selection.props.active = True
            self.pointerrow.props.sensitive = False
            self.shadowrow.props.sensitive = False
            self.delayrow.props.sensitive = False
        elif value == 'Screen':
            if not self._toggle_flag:
                self.screen.props.active = True
            self.pointerrow.props.sensitive = True
            self.shadowrow.props.sensitive = False
            self.delayrow.props.sensitive = True
        else:
            if not self._toggle_flag:
                self.window.props.active = True
            self.pointerrow.props.sensitive = True
            self.shadowrow.props.sensitive = True
            self.delayrow.props.sensitive = True
        self._toggle_flag = False

    @GtkTemplate.Callback
    def on_screen(self, btn=None):
        self._toggle_flag = True
        self.props.mode = 'Screen'

    @GtkTemplate.Callback
    def on_window(self, btn=None):
        self._toggle_flag = True
        self.props.mode = 'Window'

    @GtkTemplate.Callback
    def on_selection(self, btn=None):
        self._toggle_flag = True
        self.props.mode = 'Selection'

    def update_header(self, row, before):
        if not before:
            row.set_header(None)
            return

        current = row.get_header()
        if not current:
            current = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
            current.show()
            row.set_header(current)


@GtkTemplate(ui='/org/gnome/Kasbah/save.ui')
class SaveBox(Gtk.Box):
    __gtype_name__ = 'SaveBox'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()
