from gi.repository import Gio, GObject, GLib


class ShellService(GObject.GObject):
    BUS_NAME = "org.gnome.Shell.Screenshot"
    OBJECT_PATH = "/org/gnome/Shell/Screenshot"
    IFACE_NAME = "org.gnome.Shell.Screenshot"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Gio.bus_get(Gio.BusType.SESSION, None, self._got_conn)

    @GObject.Signal
    def ready(self):
        pass

    def _got_conn(self, s, res):
        self.conn = Gio.bus_get_finish(res)
        self.emit('ready')

    def flash(self, x, y, width, height, cb=None):
        self.conn.call(self.BUS_NAME,
                       self.OBJECT_PATH,
                       self.IFACE_NAME,
                       "FlashArea",
                       GLib.Variant("(iiii)", [x, y, width, height]),
                       None,
                       Gio.DBusCallFlags.NONE,
                       -1,
                       None,
                       self._flash_done,
                       cb)

    def _flash_done(self, src, res, cb):
        src.call_finish(res)
        if cb:
            cb()

    def select(self, cb):
        self.conn.call(self.BUS_NAME,
                       self.OBJECT_PATH,
                       self.IFACE_NAME,
                       "SelectArea",
                       None,
                       GLib.VariantType("(iiii)"),
                       Gio.DBusCallFlags.NONE,
                       -1,
                       None,
                       self._select_done,
                       cb)

    def _select_done(self, src, res, cb):
        x, y, w, h = src.call_finish(res).unpack()
        if cb:
            cb(x, y, w, h)

    def screenshot(self, filename, cursor=False, flash=True, cb=None):
        self.conn.call(self.BUS_NAME,
                       self.OBJECT_PATH,
                       self.IFACE_NAME,
                       "Screenshot",
                       GLib.Variant("(bbs)", [cursor, flash, filename]),
                       GLib.VariantType("(bs)"),
                       Gio.DBusCallFlags.NONE,
                       -1,
                       None,
                       self._screenshot_done,
                       cb)

    def area(self, filename, x, y, width, height, flash=True, cb=None):
        self.conn.call(self.BUS_NAME,
                       self.OBJECT_PATH,
                       self.IFACE_NAME,
                       "ScreenshotArea",
                       GLib.Variant("(iiiibs)",
                                    [x, y, width, height, flash, filename]),
                       GLib.VariantType("(bs)"),
                       Gio.DBusCallFlags.NONE,
                       -1,
                       None,
                       self._screenshot_done,
                       cb)

    def window(self, filename, frame=True, cursor=False, flash=True, cb=None):
        self.conn.call(self.BUS_NAME,
                       self.OBJECT_PATH,
                       self.IFACE_NAME,
                       "ScreenshotWindow",
                       GLib.Variant("(bbbs)",
                                    [frame, cursor, flash, filename]),
                       GLib.VariantType("(bs)"),
                       Gio.DBusCallFlags.NONE,
                       -1,
                       None,
                       self._screenshot_done,
                       cb)

    def _screenshot_done(self, src, res, cb):
        success, filename = src.call_finish(res).unpack()
        if cb:
            cb(success, filename)

