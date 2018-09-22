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

from gi.repository import Gtk
from .gi_composites import GtkTemplate


@GtkTemplate(ui='/org/gnome/Kasbah/window.ui')
class KasbahWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'KasbahWindow'

    capture_stack = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()

        capture = CaptureBox()
        save = SaveBox()

        self.capture_stack.add_named(capture, "capture")
        self.capture_stack.add_named(save, "save")
        self.show_all()


@GtkTemplate(ui='/org/gnome/Kasbah/capture.ui')
class CaptureBox(Gtk.Box):
    __gtype_name__ = 'CaptureBox'


    # The 3 radio buttons
    screen = GtkTemplate.Child()
    window = GtkTemplate.Child()
    selection = GtkTemplate.Child()

    # The usefull switches from the widget
    # We will need to map actions to them later
    pointer = GtkTemplate.Child()
    shadow = GtkTemplate.Child()
    delay = GtkTemplate.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()


@GtkTemplate(ui='/org/gnome/Kasbah/save.ui')
class SaveBox(Gtk.Box):
    __gtype_name__ = 'SaveBox'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()
