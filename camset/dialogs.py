import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class Dialogs:
    def hide_message(self, win):
        win.warning.set_reveal_child(False)

    def show_message(self, message, error, win):
        win.warningmessage.get_buffer().set_text("")
        color = "<span foreground='#FF0000'>" if error else "<span foreground='#00FF00'>"
        win.warningmessage.get_buffer().insert_markup(win.warningmessage.get_buffer().get_end_iter(), color + message + "</span>", -1)
        win.warning.set_reveal_child(True)
        GLib.timeout_add_seconds(2.5, self.hide_message, win)

    def load_settings_from_file(self, filename, dialog, win):
        card = win.card
        try:              
            f = open(filename, "r")
            lines = f.readlines()
            for line in lines:
                splits = line.split("=")
                setting = splits[0]
                value = splits[1]
                if (setting == "resolution_index"):
                    win.resolution_selection.set_active(int(value))
                    continue
                subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}={1}'.format(setting, value)], check=False, universal_newlines=True)
            f.close()
            self.show_message("Settings file {0} successfully loaded".format(filename), False, win)
            win.clear_and_rebuild()
        except Exception as e:
            if dialog:
                dialog.destroy()
            self.show_message("Unable to load file {0} - {1}".format(filename, e), True, win)
            return

    def add_filters(self, dialog):
        filter_config = Gtk.FileFilter()
        filter_config.set_name("Camset config files")
        filter_config.add_pattern("*.camset")
        dialog.add_filter(filter_config)

    def on_open_clicked(self, btn, win, path):
        dialog = Gtk.FileChooserDialog(
            title="Choose configuration file to load", parent=win, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)
        dialog.set_current_folder(path)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.load_settings_from_file(filename, dialog, win)
        dialog.destroy()
        
    def on_save_clicked(self, btn, win, path):
        card = win.card
        capread = subprocess.run(['v4l2-ctl', '-d', card, '-L'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
        capabilites = capread.stdout.split('\n')
        tostore = ""
        for line in capabilites:
            line = line.strip()
            if "0x" in line:
                if not "flags=inactive" in line:
                    setting = line.split('0x', 1)[0].strip()
                    value = line.split("value=", 1)[1]
                    value = int(value.split(' ', 1)[0])
                    tostore += '{0}={1}\n'.format(setting, value)
        tostore += "resolution_index={0}".format(win.resolution_selection.get_active())
        dialog = Gtk.FileChooserDialog(
            title="Save current configuration", parent=win, action=Gtk.FileChooserAction.SAVE
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE,
            Gtk.ResponseType.OK,
        )
        dialog.set_current_name("{0}.camset".format(win.cardname))
        dialog.set_do_overwrite_confirmation(True)
        dialog.set_current_folder(path)
        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            try:              
                f = open(filename, "w")
                f.write(tostore.strip())
                f.close()
                self.show_message("Settings file {0} successfully saved".format(filename), False, win)
            except:                
                dialog.destroy()
                self.show_message("Unable to save file {0}".format(filename), True, win)
                return

        dialog.destroy()