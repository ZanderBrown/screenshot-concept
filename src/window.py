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

from gi.repository import Gtk, Gio, GObject, GLib
from .gi_composites import GtkTemplate

from .save import KasbahSave
from .service import ShellService, ServiceError

from pathlib import Path


@GtkTemplate(ui='/org/gnome/Kasbah/window.ui')
class KasbahWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'KasbahWindow'
    _mode = 'Window'
    _toggle_flag = False

    # Hamburger menu
    menu = GtkTemplate.Child()

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
    pointerrow = GtkTemplate.Child()
    shadowrow = GtkTemplate.Child()
    delayrow = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("screenshot", None)
        action.connect("activate", self.on_screenshot)
        action.set_enabled(False)
        self.add_action(action)

        self.service = ShellService()
        self.service.connect('ready', lambda o: action.set_enabled(True))
        self.service.connect('error', self.service_error)

        settings = Gio.Settings.new('org.gnome.Kasbah')
        flags = Gio.SettingsBindFlags.DEFAULT
        settings.bind('include-pointer', self.pointer, 'active', flags)
        settings.bind('window-shadow', self.shadow, 'active', flags)
        settings.bind('delay', self.delay, 'value', flags)
        settings.bind('mode', self, 'mode', flags)

        self.menu.props.menu_model = self.props.application. \
            get_menu_by_id('win-menu')

        self.listbox.set_header_func(self.update_header)

    @GObject.Property(type=str, nick='Screenshot mode')
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = value
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

    def on_about(self, act, p):
        artists = ['Tobias Bernard']
        authors = ['Jordan Petridis', 'Zander Brown']
        comments = _('Save images of your screen or individual windows')
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
                                       website_label=_('Repository'))
        about_dialog.present()

    def service_error(self, src, code):
        self.show()
        err = ServiceError(code)
        if err is ServiceError.UNAVAILABLE:
            dlg = self.show_error(_('Screenshot service unavailable'),
                                  _('The GNOME Shell Screenshot service is '
                                    'required to take a screenshot'))
            dlg.show()
        elif err is ServiceError.UNKNOWN:
            dlg = self.show_error(_('Screenshot failed'),
                                  _('An unknown error occured'))
            dlg.show()

    def update_header(self, row, before):
        if not before:
            row.set_header(None)
            return

        current = row.get_header()
        if not current:
            current = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
            current.show()
            row.set_header(current)

    def show_error(self, text, secondary):
        dlg = Gtk.MessageDialog(transient_for=self,
                                modal=True,
                                message_type=Gtk.MessageType.ERROR,
                                buttons=Gtk.ButtonsType.CLOSE,
                                text=text,
                                secondary_text=secondary)
        dlg.connect('response', lambda d, r: d.destroy())
        return dlg

    def on_screenshot(self, act, p):
        parts = [GLib.get_user_cache_dir(), 'kasbah.png']
        filename = GLib.build_filenamev(parts)
        self.hide()
        if self.mode == 'Selection':
            self.service.select(self._on_select, filename)
        else:
            if self.delay.props.value > 0:
                GLib.timeout_add_seconds(int(self.delay.props.value),
                                         self._on_screenshot,
                                         filename)
            else:
                # Give the window a chance to recive focus
                GLib.timeout_add(600, self._on_screenshot, filename)

    def _on_screenshot(self, filename):
        if self.mode == 'Window':
            self.service.window(filename,
                                frame=self.shadow.props.active,
                                cursor=self.pointer.props.active,
                                cb=self.save)
        else:
            self.service.screenshot(filename,
                                    cursor=self.pointer.props.active,
                                    cb=self.save)

    def _on_select(self, x, y, w, h, filename):
        self.service.area(filename, x, y, w, h, cb=self.save)

    def save(self, success, filename, data=None):
        self.show()
        if success:
            save = KasbahSave(filename,
                              transient_for=self,
                              modal=True,
                              application=self.props.application)
            save.show()
        else:
            title = _('Screenshot failed')
            secondary = _('The screenshot service reported an error')
            dlg = self.show_error(title, secondary)
            dlg.show()
        return GLib.SOURCE_REMOVE

