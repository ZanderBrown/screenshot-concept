# save.py
#
# Copyright 2018 Zander Brown
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

from gi.repository import Gtk, Gio, GLib, GdkPixbuf
from .gi_composites import GtkTemplate

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
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(tmpfile)
            mode = GdkPixbuf.InterpType.BILINEAR
            height = self.pixbuf.props.height
            width = self.pixbuf.props.width
            ratio = width / 250
            thumb = self.pixbuf.scale_simple(250, height / ratio, mode)
            self.preview.props.pixbuf = thumb
        except:
            print('Should do something here')

        pictures = GLib.UserDirectory.DIRECTORY_PICTURES
        filename = GLib.get_user_special_dir(pictures)
        self.folder.set_filename(filename)

        now = GLib.DateTime.new_now_local()
        time = now.format("%Y-%m-%d %H-%M-%S")
        self.filename.set_text('Screenshot from {}.png'.format(time))

    def on_clipboard(self, act, p):
        Gtk.Clipboard.get_default(self.get_display()).set_image(self.pixbuf)

    def on_save(self, act, p):
        self.filename.props.sensitive = False
        self.folder.props.sensitive = False
        parts = [GLib.get_user_cache_dir(), 'kasbah.png']
        filename = GLib.build_filenamev(parts)
        source = Gio.File.new_for_path(filename)
        folder = self.folder.get_filename()
        name = self.filename.get_text()
        path = GLib.build_filenamev([folder, name])
        dest = Gio.File.new_for_path(path)
        try:
            source.move(dest, Gio.FileCopyFlags.NONE)
            self.destroy()
        except GLib.Error as err:
            self.filename.props.sensitive = True
            self.folder.props.sensitive = True
            msg = 'We where unable to save your screenshot'
            if err.matches(Gio.io_error_quark(), Gio.IOErrorEnum.EXISTS):
                msg = '\'{}\' already exists'.format(name)
            dlg = Gtk.MessageDialog(transient_for=self,
                                    modal=True,
                                    message_type=Gtk.MessageType.ERROR,
                                    buttons=Gtk.ButtonsType.CLOSE,
                                    text='Saving failed',
                                    secondary_text=msg)
            dlg.connect('response', lambda d, r: d.destroy())
            dlg.show()

