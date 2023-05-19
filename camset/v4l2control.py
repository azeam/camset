import subprocess

class V4L2Control:
    def __init__(self, win):
        self.win = win
        
    def set_value(self, setting, value, card):
        subprocess.run(['v4l2-ctl', '-d', card, '-c', '{0}={1}'.format(setting, value)], check=True, universal_newlines=True)

    def set_int_value(self, callback, setting):
        value = str(int(callback.get_value()))
        self.set_value(setting, value, self.win.card)
    
    def set_bool_value(self, callback, _active, setting):
        self.set_value(setting, 1 if callback.get_active() else 0, self.win.card)
        self.set_sensitivity()

    def on_ctrl_combo_changed(self, callback, setting): # change combobox values except resolution        
        value = callback.get_model()[callback.get_active()][0].split(": ", 1)[0] # get value from text because index is not (always) same as value
        self.set_value(setting, value, self.win.card)
        self.set_sensitivity()

    def set_sensitivity(self):
        controls = self.win.int_control_box.get_children()
        index = 0
        for line in self.get_capabilities(self.win.card):
            if "0x" in line and "int" in line:
                index += 1
                if (len(controls) > ((index -1))): # check because of error when filling ctrl_combobox at start
                    controls[(index - 1)].set_sensitive(False if "flags=inactive" else True)
                            
    def split_default_value(self, line, card):
        setting = line.split('0x', 1)[0].strip()
        value = line.split("default=", 1)[1]
        value = int(value.split(' ', 1)[0])
        self.set_value(setting, value, card)

    def get_capabilities(self, card):
        try:
            capread = subprocess.run(['v4l2-ctl', '-d', card, '-L'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
        except:
            return
        capabilites = capread.stdout.split('\n')
        return capabilites

    def set_defaults(self):
        capabilites = self.get_capabilities(self.win.card)
        for line in capabilites:
            line = line.strip()
            if "0x" in line and "int" in line and not "flags=inactive" in line:
                self.split_default_value(line, self.win.card)
                    
        for line in capabilites:
            line = line.strip()
            if "0x" in line and not "int" in line:
                self.split_default_value(line, self.win.card)               

    def set_active_resolution(self):
        curoutputread = subprocess.run(['v4l2-ctl', '-d', self.win.card, '-V'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
        curoutput = curoutputread.stdout.split('\n')
        
        for line in curoutput:
            line = line.strip()
            if "Width/Height" in line:
                split = line.split(" : ", 1)[1].strip()
                height_width = split.replace("/", "x")
            elif "Pixel Format" in line:
                pixel_format = line.split("'", 1)[1]
                pixel_format = pixel_format.split("'", 1)[0]
                combined = " - ".join((pixel_format, height_width))
        # count index, set active
        index = 0
        for item in self.win.ctrl_store:
            index += 1
            if combined in item[0]:
                break
        return (index - 1)