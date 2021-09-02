import cv2
import gi
import subprocess

# TODO: proper ioctl calls instead of using v4l2-ctl ... ?

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf

def set_video_size(callback):
    global videosize
    videosize = callback.get_value()
    
def get_active_card():
    index = win.combobox.get_active()
    model = win.combobox.get_model()
    card = model[index]
    return card[0]

def stop_camera_feed():
    global cap
    cap = None
    camwin.hide()
    win.btn_showcam.set_active(False)

def start_camera_feed(pixelformat, vfeedwidth, vfeedheight, fourcode):
    card = get_active_card()
    global cap
    global runId
    cap = None # stop stream because resolution can't be changed while running
    errorMsg = ""
    
    process = subprocess.Popen(['v4l2-ctl', '-d', card, '-v', 'height={0},width={1},pixelformat={2}'.format(vfeedheight, vfeedwidth, pixelformat)], universal_newlines=True, stdout=subprocess.PIPE)
    out, err = process.communicate()
    if process.returncode == 0:
        cap = cv2.VideoCapture(card, cv2.CAP_V4L2)
        # also set resolution to cap, otherwise cv2 will use default and not the res set by v4l2
        cap.set(3,int(vfeedwidth))
        cap.set(4,int(vfeedheight))
        cap.set(cv2.CAP_PROP_FOURCC, fourcode)
        # cap.set(5,1) 1 fps
        runId = GLib.idle_add(show_frame) 
    else: 
        if "Device or resource busy" in str(out):
            errorMsg = "Unable to start feed, the device is busy"
        elif process.returncode == 1:
            errorMsg = "Unable to start feed, not a valid output device"
        else:
            errorMsg = "Unable to start feed, unknown error"
        runId = 0       
    return errorMsg

def hide_error():
    win.warning.set_reveal_child(False)

def show_error(message):
    win.warningmessage.get_buffer().set_text("")
    win.warningmessage.get_buffer().insert_markup(win.warningmessage.get_buffer().get_end_iter(), "<span foreground='#FF0000'>" + message + "</span>", -1)
    win.warning.set_reveal_child(True)
    GLib.timeout_add_seconds(2.5, hide_error)

def init_camera_feed():
    list = get_video_resolution()
    attemptInit = start_camera_feed(list[0], list[1], list[2], list[3])
    if len(attemptInit) == 0:
        camwin.show()
        win.btn_showcam.set_active(True)
    else:
        stop_camera_feed()
        show_error(attemptInit)

def clear_and_rebuild():
    card = get_active_card()
    intcontrols = win.intcontrolbox.get_children()
    boolcontrols = win.boolcontrolbox.get_children()
    menucontrols = win.menucontrolbox.get_children()
    intlabels = win.intlabelbox.get_children()
    boollabels = win.boollabelbox.get_children()
    menulabels = win.menulabelbox.get_children()
    for item in intcontrols:
        win.intcontrolbox.remove(item)
    for item in boolcontrols:
        win.boolcontrolbox.remove(item)
    for item in menucontrols:
        win.menucontrolbox.remove(item)
    for item in menulabels:
        win.menulabelbox.remove(item)
    for item in intlabels:
        win.intlabelbox.remove(item)
    for item in boollabels:
        win.boollabelbox.remove(item)
    read_capabilites(card)

def get_video_resolution():
    index = win.res_combobox.get_active()
    model = win.res_combobox.get_model()
    text = model[index]
    res = text[0].split(" ")[-1]
    pixelformat = text[0].split(" - ", 1)[0]
    vfeedwidth = res.split("x", 1)[0]
    vfeedheight = res.split("x", 1)[1]
    fourcode = cv2.VideoWriter_fourcc(*'{}'.format(pixelformat))
    return [pixelformat, vfeedwidth, vfeedheight, fourcode]

class CamWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Camera feed")
        self.connect('delete-event', lambda w, e: stop_camera_feed() or True) # override delete and just hide window, or widgets will be destroyed
        # video     
        fixed = Gtk.Fixed()
        self.add(fixed)
        self.image_area = Gtk.Box() 
        self.videobox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.image = Gtk.Image()
        self.videobox.add(self.image_area)
        self.image_area.add(self.image)
        self.image_area.show_all()
        # videosize
        self.vidcontrolgrid = Gtk.Grid()
        self.vidcontrolgrid.set_column_homogeneous(True)
        self.label = Gtk.Label(label="Camera feed scale (percentage)")  
        self.adj = Gtk.Adjustment(value = videosize, lower = 1, upper = 100, step_increment = 1, page_increment = 1, page_size=0)
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.adj)
        self.scale.set_digits(0)
        self.scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.scale.set_margin_end(20)
        self.scale.connect("value-changed", set_video_size)
        self.vidcontrolgrid.add(self.label)
        self.vidcontrolgrid.add(self.scale)
        fixed.put(self.vidcontrolgrid, 30, 30)
        fixed.put(self.videobox, 0, 90)
        self.show_all()

class Window(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Camset")
        
        # main container
        self.layout = Gtk.ScrolledWindow()
        self.add(self.layout)
        self.grid = Gtk.Grid()
        self.layout.add(self.grid)
        self.grid.set_column_spacing(10)
        self.grid.set_row_homogeneous(False)
        self.grid.set_column_homogeneous(False)

        # boxes
        self.menulabelbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.menulabelbox.set_margin_start(20)
        self.menucontrolbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.menucontrolbox.set_margin_bottom(50)
        self.boollabelbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.boollabelbox.set_margin_start(20)
        self.boolcontrolbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.boolcontrolbox.set_margin_end(50)
        self.intlabelbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.intlabelbox.set_margin_start(20)
        self.intcontrolbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.intcontrolbox.set_margin_bottom(50)
        self.devicelabelbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.devicelabelbox.set_margin_bottom(30)
        self.devicecontrolbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.devicecontrolbox.set_margin_bottom(30)

        # combobox for device selection
        self.combobox = Gtk.ComboBox()
        self.label = Gtk.Label(label="Device")
        self.label.set_size_request(-1, 35)
        self.label.set_halign(Gtk.Align.END)
        self.devicecontrolbox.add(self.combobox)
        self.store = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        self.combobox.pack_start(cell, 25)
        self.combobox.add_attribute(cell, 'text', 0)
        self.combobox.set_model(self.store)
        self.devicelabelbox.add(self.label)

        # buttons
        self.btn_defaults = Gtk.Button(label="Load defaults", hexpand = False, vexpand = False)
        self.btn_defaults.set_size_request(-1, 35)
        self.btn_defaults.set_margin_bottom(30)
        self.btn_defaults.set_halign(Gtk.Align.END)
        self.btn_defaults.connect("clicked", self.on_btn_defaults_clicked)
        self.btn_showcam = Gtk.ToggleButton(label="Show camera feed", hexpand = False, vexpand = False)
        self.btn_showcam.set_size_request(-1, 35)
        self.btn_showcam.set_halign(Gtk.Align.CENTER)
        self.btn_showcam.set_margin_bottom(30)
        self.btn_showcam.connect("toggled", self.on_btn_showcam_toggled)

        # warning message
        self.warningcontainer = Gtk.Box(hexpand = True)
        self.warningcontainer.set_margin_bottom(10)
        self.warning = Gtk.Revealer(hexpand = True)
        self.warning.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.warning.props.transition_duration = 1250
        self.warning.set_reveal_child(False)
        self.warningmessage = Gtk.TextView()
        self.warningmessage.set_editable(False)
        self.warningmessage.set_left_margin(10)
        self.warningmessage.set_right_margin(10)
        self.warningmessage.set_top_margin(5)
        self.warningmessage.set_bottom_margin(5)
        self.warningmessage.props.halign = Gtk.Align.CENTER
        self.warning.add(self.warningmessage)
        self.warningcontainer.add(self.warning)

        # set up grid
        self.grid.add(self.devicelabelbox)
        self.grid.attach_next_to(self.warningcontainer, self.devicelabelbox, Gtk.PositionType.TOP, 30, 1)
        self.grid.attach_next_to(self.devicecontrolbox, self.devicelabelbox, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.btn_defaults, self.devicecontrolbox, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.btn_showcam, self.btn_defaults, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.menulabelbox, self.devicelabelbox, Gtk.PositionType.BOTTOM, 1, 1)
        self.grid.attach_next_to(self.menucontrolbox, self.menulabelbox, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.intlabelbox, self.menucontrolbox, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.intcontrolbox, self.intlabelbox, Gtk.PositionType.RIGHT, 20, 1)
        self.grid.attach_next_to(self.boollabelbox, self.intcontrolbox, Gtk.PositionType.RIGHT, 1, 1)
        self.grid.attach_next_to(self.boolcontrolbox, self.boollabelbox, Gtk.PositionType.RIGHT, 1, 1)
        
    def on_btn_showcam_toggled(self, widget):
        if widget.get_active() and not camwin.props.visible:
            init_camera_feed()
        elif widget.get_active() and camwin.props.visible:
            pass
        else:
            stop_camera_feed()

    def on_btn_defaults_clicked(self, widget):
        card = get_active_card()
        capread = subprocess.run(['v4l2-ctl', '-d', card, '-L'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
        capabilites = capread.stdout.split('\n')
        for line in capabilites:
            line = line.strip()
            if "0x" in line:
                if not "flags=inactive" in line:
                    setting = line.split('0x', 1)[0].strip()
                    value = line.split("default=", 1)[1]
                    value = int(value.split(' ', 1)[0])
                    subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}={1}'.format(setting, value)], check=False, universal_newlines=True)
        win.res_combobox.set_active(0) # first option is default
        clear_and_rebuild()

    def on_device_changed(self, widget):
        stop_camera_feed() 
        # stopping feed is not (always) enough to kill the idle process, remove if set
        global runId
        if runId > 0:
            GLib.source_remove(runId)
        card = get_active_card()
        try:
            devnameread = subprocess.run(['v4l2-ctl', '-d', card, '-D'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
            devnameline = devnameread.stdout.split('\n')
            for line in devnameline:
                if "Card type" in line:
                    cardname = line.split(': ', 1)[1].strip()
                    if len(cardname) > 0:
                        win.set_title(title="Camset - {}".format(cardname))
                        camwin.set_title(title="Camera feed - {}".format(cardname))
                    else:
                        win.set_title(title="Camset")
                        camwin.set_title(title="Camera feed")
        except:
            runId = 0
            pass
        clear_and_rebuild()
        init_camera_feed()

def set_int_value(callback, card, setting):
    value = str(int(callback.get_value()))
    subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}={1}'.format(setting, value)], check=True, universal_newlines=True)
    
def set_bool_value(callback, active, card, setting):
    if callback.get_active():
        subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}=1'.format(setting)], check=True, universal_newlines=True)
    else:
        subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}=0'.format(setting)], check=True, universal_newlines=True)
    set_sensitivity(card)

def on_ctrl_combo_changed(callback, card, setting): # change combobox values except resolution
    index = callback.get_active()
    model = callback.get_model()
    value = model[index]
    value = value[0].split(": ", 1)[0] # get value from text because index is not (always) same as value
    subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}={1}'.format(setting, value)], check=True, universal_newlines=True)
    set_sensitivity(card)
    
def on_output_combo_changed(callback, card): # change resolution
    if (camwin.props.visible):
        stop_camera_feed()
        # cap never gets reset to none when initing the feed again, causing it to run twice, manually remove runId if set
        global runId
        if runId > 0:
            GLib.source_remove(runId)
        init_camera_feed()  

def set_sensitivity(card):
    capread = subprocess.run(['v4l2-ctl', '-d', card, '-L'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
    capabilites = capread.stdout.split('\n')
    controls = win.intcontrolbox.get_children()
    index = 0
    for line in capabilites:
        if "0x" in line:
            if "int" in line:
                index += 1
                if (len(controls) > ((index -1))): # check because of error when filling ctrl_combobox at start
                    if "flags=inactive" in line:
                        controls[(index - 1)].set_sensitive(False)
                    else:
                        controls[(index - 1)].set_sensitive(True)

def read_resolution_capabilites(card):
    outputread = subprocess.run(['v4l2-ctl', '-d', card, '--list-formats-ext'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
    outputs = outputread.stdout.split('\n')
    showcombo = False
    pre = ''
    post = ''
    win.ctrl_store = Gtk.ListStore(str)
    for line in outputs:
        if ":" in line:
            line = line.strip()
            if "'" in line:
                pre = line.split("'", 1)[1]
                pre = pre.split("'", 1)[0]
            else:
                if "Size:" in line:
                    post = line.split("Size: ", 1)[1]
                    post = post.split(" ")[-1]
                    output = " - ".join((pre, post))
                    win.ctrl_store.append([output])
                    showcombo = True
    if showcombo == True:
        win.label = Gtk.Label(hexpand = True, vexpand = False)
        win.label.set_text("Video Resolution")
        win.label.set_size_request(-1, 35)
        win.label.set_halign(Gtk.Align.END)
        win.res_combobox = Gtk.ComboBox()
        win.res_combobox.set_size_request(-1, 35)
        cell = Gtk.CellRendererText()
        win.res_combobox.pack_start(cell, 25)
        win.res_combobox.add_attribute(cell, 'text', 0)
        win.res_combobox.set_model(win.ctrl_store)
        win.res_combobox.connect('changed', on_output_combo_changed, card)
        win.menucontrolbox.pack_start(win.res_combobox, False, False, 0)
        win.menulabelbox.pack_start(win.label, False, False, 0)
        # find item in combobox that equals current value and set active
        curoutputread = subprocess.run(['v4l2-ctl', '-d', card, '-V'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
        curoutput = curoutputread.stdout.split('\n')
        hewi = ''
        pf = ''
        strcheck = ''
        for line in curoutput:
            line = line.strip()
            if "Width/Height" in line:
                split = line.split(" : ", 1)[1].strip()
                hewi = split.replace("/", "x")
            elif "Pixel Format" in line:
                pf = line.split("'", 1)[1]
                pf = pf.split("'", 1)[0]
                strcheck = " - ".join((pf, hewi))
        # count index, set active
        index = 0
        for item in win.ctrl_store:
            index += 1
            if strcheck in item[0]:
                break
        win.res_combobox.set_active(index - 1)

def read_capabilites(card):
    try:
        capread = subprocess.run(['v4l2-ctl', '-d', card, '-L'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
    except:
        return
    capabilites = capread.stdout.split('\n')
    menvalue = 0 # set menvalue when scanning menu to be able to read from menu options
    for line in capabilites:
        line = line.strip()
        if line == "User Controls":
            continue
        elif line == "Camera Controls":
            continue
        elif "0x" in line:
            setting = line.split('0x', 1)[0].strip()
            label = str.replace(setting, '_', ' ').title()
            value = line.split("value=", 1)[1]
            value = int(value.split(' ', 1)[0])
            win.label = Gtk.Label(hexpand = True, vexpand = False)
            win.label.set_text(label)
            win.label.set_size_request(-1, 35)
            win.label.set_halign(Gtk.Align.END)
            
            if "int" in line:
                upper = line.split("max=", 1)[1]
                upper = int(upper.split(' ', 1)[0])
                lower = line.split("min=", 1)[1]
                lower = int(lower.split(' ', 1)[0])
                step = line.split("step=", 1)[1]
                step = int(step.split(' ', 1)[0])

                adj = Gtk.Adjustment(value = value, lower = lower, upper = upper, step_increment = step, page_increment = 1, page_size=0)
                win.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
                win.scale.set_digits(0)
                win.scale.set_value_pos(Gtk.PositionType.RIGHT)
                win.scale.set_size_request(-1, 35)
                win.scale.connect("value-changed", set_int_value, card, setting)
                win.intcontrolbox.pack_start(win.scale, False, False, 0)
                win.intlabelbox.pack_start(win.label, False, False, 0)
                    
            if "bool" in line:                
                win.switch = Gtk.Switch(hexpand = False, vexpand = False)
                if value == 1:
                    win.switch.set_active(True)
                else:
                    win.switch.set_active(False)
                win.switch.connect ("notify::active", set_bool_value, card, setting)
                win.label.set_size_request(-1, 25)
                win.switch.set_size_request(-1, 25)
                win.boolcontrolbox.pack_start(win.switch, False, False, 0)
                win.boollabelbox.pack_start(win.label, False, False, 0)
                win.switch.set_halign(Gtk.Align.START)
                win.switch.set_valign(Gtk.Align.CENTER)

            if "menu" in line:
                menvalue = value
                win.ctrl_combobox = Gtk.ComboBox()
                win.ctrl_combobox.set_size_request(-1, 35)
                win.ctrl_store = Gtk.ListStore(str)
                cell = Gtk.CellRendererText()
                win.ctrl_combobox.pack_start(cell, 25)
                win.ctrl_combobox.add_attribute(cell, 'text', 0)
                win.ctrl_combobox.set_model(win.ctrl_store)
                win.ctrl_combobox.connect('changed', on_ctrl_combo_changed, card, setting)
                win.menucontrolbox.pack_start(win.ctrl_combobox, False, False, 0)
                win.menulabelbox.pack_start(win.label, False, False, 0)
        
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

    read_resolution_capabilites(card)
    win.show_all()
    set_sensitivity(card)
                
def check_devices():
    devices = subprocess.run(['v4l2-ctl', '--list-devices'], check=False, universal_newlines=True, stdout=subprocess.PIPE)
    i = 0
    for line in devices.stdout.split('\n'):
        if "dev" in line:
            line = line.strip()
            win.store.append ([line])
            i += 1
    win.combobox.connect('changed', win.on_device_changed) # start after populating devices or action will be called when adding
    if (i > 0):
        win.combobox.set_active(0)

def show_frame():
    global cap
    if cap is None:
        return False
    ret, frame = cap.read()
    if frame is not None:
        width = int(frame.shape[1] * videosize / 100)
        height = int(frame.shape[0] * videosize / 100)
        dim = (width, height)
        # TODO: resizing video and window this way is very cpu intensive for large resolutions, should be improved or removed
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_CUBIC)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # needed for proper color representation in gtk
        pb = GdkPixbuf.Pixbuf.new_from_data(frame.tostring(),
                                            GdkPixbuf.Colorspace.RGB,
                                            False,
                                            8,
                                            frame.shape[1],
                                            frame.shape[0],
                                            frame.shape[2]*frame.shape[1]) # last argument is "rowstride (int) - Distance in bytes between row starts" (??)
        camwin.image.set_from_pixbuf(pb.copy())
    camwin.resize(1, 1)
    return True

def main():
    camwin.hide()
    check_devices()
    win.resize(win.grid.get_allocation().width, win.grid.get_allocation().height + 20) # hardcoded extra margin seems needed to not show scrollbars, not sure where space is coming from
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

runId = 0
cap = None
videosize = 100
win = Window()
camwin = CamWindow()

if __name__ == "__main__":
    main()
