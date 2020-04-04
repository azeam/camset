import cv2
import gi
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf

cap = None
videosize = 40

def set_video_size(callback):
    global videosize
    videosize = callback.get_value()

class Window(Gtk.Window):
    def __init__(self):
        # TODO: scrolled window and better alignment of boxes 
        Gtk.Window.__init__(self, title="Camset")
        
        # main container
        fixed = Gtk.Fixed()
        self.add(fixed)

        # combobox for device selection
        self.combobox = Gtk.ComboBox()
        fixed.put(self.combobox, 30, 30)
        self.store = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        self.combobox.pack_start(cell, 25)
        self.combobox.add_attribute(cell, 'text', 0)
        self.combobox.set_model(self.store)
        self.combobox.connect('changed', self.on_device_changed)

        # box for videosize
        self.vidcontrolbox = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        fixed.put(self.vidcontrolbox, 30, 80)
        self.label = Gtk.Label(label="Video size (percentage)")  
        self.adj = Gtk.Adjustment(value = videosize, lower = 1, upper = 100, step_increment = 1, page_increment = 5, page_size=0)
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.adj)
        self.scale.set_digits(0)
        self.scale.connect("value-changed", set_video_size)
        self.vidcontrolbox.add(self.scale)
        self.vidcontrolbox.add(self.label)

        # video and controls
        self.videobox = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        fixed.put(self.videobox, 30, 190)
        self.image_area = Gtk.Box()        
        self.image = Gtk.Image()
        self.videobox.add(self.image_area)
        self.image_area.add(self.image)
        self.image_area.show_all()

        # container for menu controls
        self.menucontrolbox = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        fixed.put(self.menucontrolbox, 255, 30)
        
        # container for bool controls
        self.boolcontrolbox = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        fixed.put(self.boolcontrolbox, 525, 30)

        # container for int controls
        self.controlbox = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        fixed.put(self.controlbox, 795, 30)
        self.controlbox.set_margin_end(100)

    def on_device_changed(self, widget):
        index = self.combobox.get_active()
        model = self.combobox.get_model()
        card = model[index]
        controls = self.controlbox.get_children()
        boolcontrols = self.boolcontrolbox.get_children()
        menucontrols = self.menucontrolbox.get_children()
        # clear all items and rebuild on device change
        for item in controls:
            self.controlbox.remove(item)
        for item in boolcontrols:
            self.boolcontrolbox.remove(item)
        for item in menucontrols:
            self.menucontrolbox.remove(item)
        
        global cap
        cap = cv2.VideoCapture(card[0], cv2.CAP_V4L2)
        read_capabilites(card[0])

win = Window()

def set_int_value(callback, card, setting):
    value = str(int(callback.get_value()))
    subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}={1}'.format(setting, value)], check=True, text=True)
    
def set_bool_value(callback, active, card, setting):
    if callback.get_active():
        subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}=1'.format(setting)], check=True, text=True)
    else:
        subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}=0'.format(setting)], check=True, text=True)
    set_sensitivity(card)

def on_ctrl_combo_changed(callback, card, setting): # aka set_menu_value
    index = callback.get_active()
    model = callback.get_model()
    value = model[index]
    value = value[0].split(": ", 1)[0] # get value from text because index is not (always) same as value
    subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}={1}'.format(setting, value)], check=True, text=True)
    set_sensitivity(card)
    
def set_sensitivity(card):
    capread = subprocess.run(['v4l2-ctl', '-d', card, '-L'], check=True, text=True, stdout=subprocess.PIPE)
    capabilites = capread.stdout.split('\n')
    controls = win.controlbox.get_children()
    index = 0
    for line in capabilites:
        if "0x" in line:
            if "int" in line:
                index += 1
                if (len(controls) > ((index -1) * 2)): # check because of error when filling ctrl_combobox at start
                    if "flags=inactive" in line:
                        controls[(index - 1) * 2].set_sensitive(False) # control has twice as many items as index (-1) because of the labels
                    else:
                        controls[(index - 1) * 2].set_sensitive(True)

def read_capabilites(card):
    capread = subprocess.run(['v4l2-ctl', '-d', card, '-L'], check=True, text=True, stdout=subprocess.PIPE)
    capabilites = capread.stdout.split('\n')
    menvalue = 0 # set menvalue when scanning menu to be able to read from menu options
    for line in capabilites:
        line = line.strip()
        if "0x" in line:
            setting = line.split('0x', 1)[0].strip()
            label = str.replace(setting, '_', ' ').title()
            value = line.split("value=", 1)[1]
            value = int(value.split(' ', 1)[0])
            win.label = Gtk.Label()
            win.label.set_text(label)
            win.label.set_margin_bottom(20)

            if "int" in line:
                upper = line.split("max=", 1)[1]
                upper = int(upper.split(' ', 1)[0])
                lower = line.split("min=", 1)[1]
                lower = int(lower.split(' ', 1)[0])
                step = line.split("step=", 1)[1]
                step = int(step.split(' ', 1)[0])

                adj = Gtk.Adjustment(value = value, lower = lower, upper = upper, step_increment = step, page_increment = 5, page_size=0)
                win.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
                win.scale.set_digits(0)
                win.scale.connect("value-changed", set_int_value, card, setting)
                win.controlbox.pack_start(win.scale, True, True, 0)
                win.controlbox.pack_start(win.label, True, True, 0)
                win.label.show()
                win.scale.show()
                    
            if "bool" in line:                
                win.switch = Gtk.Switch(hexpand = False, vexpand = False)
                if value == 1:
                    win.switch.set_active(True)
                else:
                    win.switch.set_active(False)
                win.switch.connect ("notify::active", set_bool_value, card, setting)
                win.boolcontrolbox.pack_start(win.switch, True, True, 0)
                win.boolcontrolbox.pack_start(win.label, True, True, 0)
                win.switch.set_halign(Gtk.Align.CENTER)
                win.switch.show()
                win.label.show()

            if "menu" in line:
                menvalue = value
                win.ctrl_combobox = Gtk.ComboBox()
                win.ctrl_store = Gtk.ListStore(str)
                cell = Gtk.CellRendererText()
                win.ctrl_combobox.pack_start(cell, 25)
                win.ctrl_combobox.add_attribute(cell, 'text', 0)
                win.ctrl_combobox.set_model(win.ctrl_store)
                win.ctrl_combobox.connect('changed', on_ctrl_combo_changed, card, setting)
                win.menucontrolbox.pack_start(win.ctrl_combobox, True, True, 0)
                win.menucontrolbox.pack_start(win.label, True, True, 0)
                win.ctrl_combobox.show()
                win.label.show()
        
        # menu options
        else: 
            if line:
                # map index to value
                value = int(line.split(": ", 1)[0]) # get value from text because index is not (always) same as value
                win.ctrl_store.append ([line])
                # count index, set active
                index = 0
                for item in win.ctrl_store:
                    index += 1
                if value == menvalue:
                    win.ctrl_combobox.set_active(index - 1)
    
    set_sensitivity(card)
                
def check_devices():
    devices = subprocess.run(['v4l2-ctl', '--list-devices'], check=True, text=True, stdout=subprocess.PIPE)
    for line in devices.stdout.split('\n'):
        if "dev" in line:
            line = line.strip()
            win.store.append ([line])
            win.combobox.set_active(0)

def show_frame():
    ret, frame = cap.read()
    if frame is not None:
        width = int(frame.shape[1] * videosize / 100)
        height = int(frame.shape[0] * videosize / 100)
        dim = (width, height)
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_CUBIC)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # needed for proper color representation in gtk
        pb = GdkPixbuf.Pixbuf.new_from_data(frame.tostring(),
                                            GdkPixbuf.Colorspace.RGB,
                                            False,
                                            8,
                                            frame.shape[1],
                                            frame.shape[0],
                                            frame.shape[2]*frame.shape[1]) # last argument is "rowstride (int) – Distance in bytes between row starts" (??)
        win.image.set_from_pixbuf(pb.copy())
    else:
        cap.release()
        cv2.destroyAllWindows()
        win.image.clear()
    # TODO: add option to enable/disable cam output
    return True

def main():
    check_devices()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    GLib.idle_add(show_frame)
    Gtk.main()

if __name__ == "__main__":
    main()