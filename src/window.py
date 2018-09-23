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

from gi.repository import Gtk, Gio, GObject, GLib, GdkPixbuf
from .gi_composites import GtkTemplate

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
        self.add_action(action)

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

    def update_header(self, row, before):
        if not before:
            row.set_header(None)
            return

        current = row.get_header()
        if not current:
            current = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
            current.show()
            row.set_header(current)

    def watch(self, pid, status):
        self.show()
        if status is not 0:
            title = 'Screenshot failed'
            secondary = 'gnome-screenshot returned a non-zero status'
            dlg = Gtk.MessageDialog(transient_for=self,
                                    modal=True,
                                    message_type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.CLOSE,
                                    text=title,
                                    secondary_text=secondary)
            dlg.connect('response', lambda d, r: d.destroy())
            dlg.show()
        else:
            save = KasbahSave(transient_for=self,
                              modal=True,
                              application=self.props.application)
            save.show()

    def on_screenshot(self, act, p):
        parts = [GLib.get_user_cache_dir(), 'kasbah.png']
        filename = GLib.build_filenamev(parts)
        args = []
        if Path('/.flatpak-info').exists():
            prog = GLib.find_program_in_path('flatpak-spawn')
            args.extend([prog, '--host', 'gnome-screenshot'])
        else:
            prog = GLib.find_program_in_path('gnome-screenshot')
            args.append(prog)
        if self.mode == 'Window':
            args.append('-w')
            if self.shadow.props.active:
                args.extend(['-e', 'shadow'])
        elif self.mode == 'Selection':
            args.append('-a')
        if not self.mode == 'Selection':
            if self.pointer.props.active:
                args.append('-p')
            if self.delay.props.value > 0:
                args.extend(['-d', str(int(self.delay.props.value))])
        args.extend(['-f', filename])
        print('Launching ' + ' '.join(args))
        try:
            self.hide()
            flags = GLib.SpawnFlags.DO_NOT_REAP_CHILD
            (pid, sin, sout, serr) = GLib.spawn_async(args, flags=flags)
            GLib.child_watch_add(GLib.PRIORITY_DEFAULT_IDLE, pid, self.watch)
        except:
            self.show()
            title = 'Screenshot failed'
            secondary = 'Failed to launch gnome-screenshot'
            dlg = Gtk.MessageDialog(transient_for=self,
                                    modal=True,
                                    message_type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.CLOSE,
                                    text=title,
                                    secondary_text=secondary)
            dlg.connect('response', lambda d, r: d.destroy())
            dlg.show()


@GtkTemplate(ui='/org/gnome/Kasbah/save.ui')
class KasbahSave(Gtk.ApplicationWindow):
    __gtype_name__ = 'KasbahSave'

    preview = GtkTemplate.Child()
    filename = GtkTemplate.Child()
    folder = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        action = Gio.SimpleAction.new("cancel", None)
        action.connect("activate", lambda a, p: self.destroy())
        self.add_action(action)

        action = Gio.SimpleAction.new("clipboard", None)
        action.connect("activate", self.on_clipboard)
        self.add_action(action)

        action = Gio.SimpleAction.new("save", None)
        action.connect("activate", self.on_save)
        self.add_action(action)

        try:
            parts = [GLib.get_user_cache_dir(), 'kasbah.png']
            tmpfile = GLib.build_filenamev(parts)
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(tmpfile)
            mode = GdkPixbuf.InterpType.BILINEAR
            height = pixbuf.props.height
            width = pixbuf.props.width
            ratio = width / 250
            pixbuf = pixbuf.scale_simple(250, height / ratio, mode)
            self.preview.props.pixbuf = pixbuf
        except:
            print('Should do something here')

        pictures = GLib.UserDirectory.DIRECTORY_PICTURES
        filename = GLib.get_user_special_dir(pictures)
        self.folder.set_filename(filename)

        now = GLib.DateTime.new_now_local()
        time = now.format("%Y-%m-%d %H-%M-%S")
        self.filename.set_text('Screenshot from {}.png'.format(time))

    def on_clipboard(self, act, p):
        pass

    def on_save(self, act, p):
        pass
