from typing import Optional

from gi.repository import Gtk


class OpenFileDialog(Gtk.FileChooserDialog):
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="Choose config file", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        self.set_local_only(True)
        self.show_all()

    @classmethod
    def open(cls, parent) -> Optional[str]:
        dialog = cls(parent)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("MSI config files")
        filter_any.add_pattern("*.msic")
        dialog.add_filter(filter_any)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            result = dialog.get_filename()
            dialog.destroy()
            return result
        else:
            dialog.destroy()
