import gi
import subprocess
import pathlib
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from camset.cam_window import CamWindow
from camset.dialogs import Dialogs
from camset.helpers import Helpers
from camset.v4l2control import V4L2Control
from camset.layout import Layout
class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Camset")
        self.cardname = ""
        layout = Layout(self, dialogs)
        layout.setup_main_container()
        layout.setup_boxes()
        layout.setup_device_selection_box()
        layout.setup_buttons()        
        layout.setup_warning_container()    
        layout.setup_toolbar(helpers.get_config_path(), V4L2Control(self))
        layout.setup_grid()
        self.layout = layout

    def clear_and_rebuild(self):
        intcontrols = self.int_control_box.get_children()
        boolcontrols = self.bool_control_box.get_children()
        menucontrols = self.menu_control_box.get_children()
        intlabels = self.int_label_box.get_children()
        boollabels = self.bool_label_box.get_children()
        menulabels = self.menu_label_box.get_children()
        for item in intcontrols:
            self.int_control_box.remove(item)
        for item in boolcontrols:
            self.bool_control_box.remove(item)
        for item in menucontrols:
            self.menu_control_box.remove(item)
        for item in menulabels:
            self.menu_label_box.remove(item)
        for item in intlabels:
            self.int_label_box.remove(item)
        for item in boollabels:
            self.bool_label_box.remove(item)
        self.read_capabilites()
        if self.read_resolution_capabilites():
            self.layout.setup_resolution()
            self.resolution_selection.set_active(v4l2_control.set_active_resolution())            
        self.show_all()
        v4l2_control.set_sensitivity()
        
    def on_btn_showcam_toggled(self, widget):
        if widget.get_active() and not camwin.props.visible:
            camwin.init_camera_feed(helpers.get_video_resolution(self))
        elif widget.get_active() and camwin.props.visible:
            pass
        else:
            camwin.stop_camera_feed()

    def on_btn_defaults_clicked(self, _widget):
        v4l2_control.set_defaults()
        self.resolution_selection.set_active(0) # first option is default
        self.clear_and_rebuild()

    def on_device_changed(self, _widget):
        camwin.stop_camera_feed() 
        self.card = helpers.get_active_card(self)
        self.cardname = helpers.get_card_name(self.card)
        subtitle = " - {}".format(self.cardname) if len(self.cardname) > 0 else ""
        self.set_title(title="Camset{}".format(subtitle))
        camwin.set_title(title="Camera feed{}".format(subtitle))
        
        self.clear_and_rebuild()
        configfile = helpers.get_config_path() + "/" + self.cardname + ".camset"
        if (os.path.exists(configfile) and self.autoload_checkbutton.get_active() and self.read_resolution_capabilites()):
            dialogs.load_settings_from_file(configfile, None, self, v4l2_control)
        self.btn_showcam.set_active(True)

    def on_resolution_changed(self, _callback):
        if (camwin.props.visible):
            camwin.stop_camera_feed()
        self.btn_showcam.set_active(True)

    def read_resolution_capabilites(self):
        outputread = subprocess.run(['v4l2-ctl', '-d', self.card, '--list-formats-ext'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
        outputs = outputread.stdout.split('\n')
        has_resolution_capability = False
        self.ctrl_store = Gtk.ListStore(str)
        for line in outputs:
            if ":" in line:
                line = line.strip()
                if "'" in line:
                    pre = line.split("'", 1)[1].split("'", 1)[0]
                else:
                    if "Size:" in line:
                        post = line.split("Size: ", 1)[1].split(" ")[-1]
                        output = " - ".join((pre, post))
                        self.ctrl_store.append([output])
                        has_resolution_capability = True
        return has_resolution_capability

    def read_capabilites(self):
        capabilities = v4l2_control.get_capabilities(self.card)
        menu_value = 0 # set menu value when scanning menu to be able to read from menu options
        for line in capabilities:
            line = line.strip()
            if line == "User Controls":
                continue
            elif line == "Camera Controls":
                continue
            elif "0x" in line:
                setting = line.split('0x', 1)[0].strip()
                label_text = str.replace(setting, '_', ' ').title()
                value = line.split("value=", 1)[1]
                value = int(value.split(' ', 1)[0])
                label = Gtk.Label(hexpand = True, vexpand = False)
                label.set_text(label_text)
                label.set_size_request(-1, 35)
                label.set_halign(Gtk.Align.END)
                
                if "int" in line:
                    self.layout.add_int_item(line, setting, value, v4l2_control.set_int_value)  
                    self.int_label_box.pack_start(label, False, False, 0)                  
                        
                if "bool" in line: 
                    self.layout.add_bool_item(setting, value, v4l2_control.set_bool_value)               
                    label.set_size_request(-1, 25)
                    self.bool_label_box.pack_start(label, False, False, 0)
                
                if "menu" in line:
                    menu_value = value
                    self.layout.add_menu_item(setting, v4l2_control.on_ctrl_combo_changed)
                    self.menu_label_box.pack_start(label, False, False, 0)
            
            # menu options
            elif line:
                # map index to value
                value = int(line.split(": ", 1)[0]) # get value from text because index is not (always) same as value
                self.ctrl_store.append ([line])
                # count index, set active
                index = 0
                for item in self.ctrl_store:
                    index += 1
                if value == menu_value:
                    self.ctrl_combobox.set_active(index - 1)
                    
    def check_devices(self):
        devices = subprocess.run(['v4l2-ctl', '--list-devices'], check=False, universal_newlines=True, stdout=subprocess.PIPE)
        i = 0
        for line in devices.stdout.split('\n'):
            if "dev" in line:
                line = line.strip()
                capabilities = v4l2_control.get_capabilities(line)
                if capabilities is not None and len(capabilities) > 1:
                    self.store.append(["{0} - {1}".format(line, helpers.get_card_name(line))])
                    i += 1
        self.device_selection.connect('changed', self.on_device_changed) # start after populating devices or action will be called when adding
        if (i > 0):
            self.device_selection.set_active(0)

def main():
    pathlib.Path(helpers.get_config_path()).mkdir(parents=True, exist_ok=True)
    camwin.hide()
    win.check_devices()
    win.resize(win.grid.get_allocation().width, win.grid.get_allocation().height + 20) # hardcoded extra margin seems needed to not show scrollbars, not sure where space is coming from
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

helpers = Helpers()
dialogs = Dialogs()
win = Window()
v4l2_control = V4L2Control(win)
camwin = CamWindow(win, dialogs)

if __name__ == "__main__":
    main()
