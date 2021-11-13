import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Layout:
    def __init__(self, win, dialogs):
        self.win = win
        self.dialogs = dialogs

    def setup_main_container(self):
        self.win.layout = Gtk.ScrolledWindow()
        self.win.add(self.win.layout)
        self.win.grid = Gtk.Grid()
        self.win.layout.add(self.win.grid)
        self.win.grid.set_column_spacing(10)
        self.win.grid.set_row_homogeneous(False)
        self.win.grid.set_column_homogeneous(False)

    def setup_boxes(self):
        self.win.menu_label_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.win.menu_label_box.set_margin_start(20)
        self.win.menu_control_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.win.menu_control_box.set_margin_bottom(50)
        self.win.bool_label_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.win.bool_label_box.set_margin_start(20)
        self.win.bool_control_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.win.bool_control_box.set_margin_end(50)
        self.win.int_label_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.win.int_label_box.set_margin_start(20)
        self.win.int_control_box = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.win.int_control_box.set_margin_bottom(50)
        self.win.devicelabelbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.win.devicelabelbox.set_margin_bottom(30)
        self.win.devicecontrolbox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.win.devicecontrolbox.set_margin_bottom(30)

    def setup_device_selection_box(self):
        self.win.device_selection = Gtk.ComboBox()
        self.win.label = Gtk.Label(label="Device")
        self.win.label.set_size_request(-1, 35)
        self.win.label.set_halign(Gtk.Align.END)
        self.win.devicecontrolbox.add(self.win.device_selection)
        self.win.store = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        self.win.device_selection.pack_start(cell, 25)
        self.win.device_selection.add_attribute(cell, 'text', 0)
        self.win.device_selection.set_model(self.win.store)
        self.win.devicelabelbox.add(self.win.label)

    def setup_buttons(self):
        self.win.btn_defaults = Gtk.Button(label="Load defaults", hexpand = False, vexpand = False)
        self.win.btn_defaults.set_size_request(-1, 35)
        self.win.btn_defaults.set_margin_bottom(30)
        self.win.btn_defaults.set_halign(Gtk.Align.END)
        self.win.btn_defaults.connect("clicked", self.win.on_btn_defaults_clicked)
        self.win.btn_showcam = Gtk.ToggleButton(label="Show camera feed", hexpand = False, vexpand = False)
        self.win.btn_showcam.set_size_request(-1, 35)
        self.win.btn_showcam.set_halign(Gtk.Align.CENTER)
        self.win.btn_showcam.set_margin_bottom(30)
        self.win.btn_showcam.connect("toggled", self.win.on_btn_showcam_toggled)

    def setup_warning_container(self):
        self.win.warningcontainer = Gtk.Box(hexpand = True)
        self.win.warningcontainer.set_margin_bottom(10)
        self.win.warning = Gtk.Revealer(hexpand = True)
        self.win.warning.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.win.warning.props.transition_duration = 1250
        self.win.warning.set_reveal_child(False)
        self.win.warningmessage = Gtk.TextView()
        self.win.warningmessage.set_editable(False)
        self.win.warningmessage.set_left_margin(10)
        self.win.warningmessage.set_right_margin(10)
        self.win.warningmessage.set_top_margin(5)
        self.win.warningmessage.set_bottom_margin(5)
        self.win.warningmessage.props.halign = Gtk.Align.CENTER
        self.win.warning.add(self.win.warningmessage)
        self.win.warningcontainer.add(self.win.warning)

    def setup_toolbar(self, path):
        openbtn = Gtk.ToolButton()
        openbtn.set_label("Load settings")
        openbtn.set_is_important(True)
        openbtn.set_icon_name("gtk-open")
        openbtn.connect('clicked', self.dialogs.on_open_clicked, self.win, path)
        
        savebtn = Gtk.ToolButton()
        savebtn.set_label("Save settings")
        savebtn.set_is_important(True)
        savebtn.set_icon_name("gtk-save")
        savebtn.connect('clicked', self.dialogs.on_save_clicked, self.win, path)
        
        self.win.autoload_checkbutton = Gtk.ToggleToolButton()
        self.win.autoload_checkbutton.set_label("Autoload settings")
        self.win.autoload_checkbutton.set_active(True)

        self.win.toolbar = Gtk.Toolbar()
        self.win.toolbar.add(openbtn)
        self.win.toolbar.add(savebtn)
        self.win.toolbar.add(self.win.autoload_checkbutton)

    def setup_grid(self):
        self.win.grid.add(self.win.devicelabelbox)
        self.win.grid.attach_next_to(self.win.warningcontainer, self.win.devicelabelbox, Gtk.PositionType.TOP, 30, 1)
        self.win.grid.attach_next_to(self.win.devicecontrolbox, self.win.devicelabelbox, Gtk.PositionType.RIGHT, 1, 1)
        self.win.grid.attach_next_to(self.win.btn_defaults, self.win.devicecontrolbox, Gtk.PositionType.RIGHT, 1, 1)
        self.win.grid.attach_next_to(self.win.btn_showcam, self.win.btn_defaults, Gtk.PositionType.RIGHT, 1, 1)
        self.win.grid.attach_next_to(self.win.toolbar, self.win.warningcontainer, Gtk.PositionType.TOP, 30, 1)
        self.win.grid.attach_next_to(self.win.menu_label_box, self.win.devicelabelbox, Gtk.PositionType.BOTTOM, 1, 1)
        self.win.grid.attach_next_to(self.win.menu_control_box, self.win.menu_label_box, Gtk.PositionType.RIGHT, 1, 1)
        self.win.grid.attach_next_to(self.win.int_label_box, self.win.menu_control_box, Gtk.PositionType.RIGHT, 1, 1)
        self.win.grid.attach_next_to(self.win.int_control_box, self.win.int_label_box, Gtk.PositionType.RIGHT, 20, 1)
        self.win.grid.attach_next_to(self.win.bool_label_box, self.win.int_control_box, Gtk.PositionType.RIGHT, 1, 1)
        self.win.grid.attach_next_to(self.win.bool_control_box, self.win.bool_label_box, Gtk.PositionType.RIGHT, 1, 1)

    def setup_resolution(self):
        self.win.label = Gtk.Label(hexpand = True, vexpand = False)
        self.win.label.set_text("Video Resolution")
        self.win.label.set_size_request(-1, 35)
        self.win.label.set_halign(Gtk.Align.END)
        self.win.resolution_selection = Gtk.ComboBox()
        self.win.resolution_selection.set_size_request(-1, 35)
        cell = Gtk.CellRendererText()
        self.win.resolution_selection.pack_start(cell, 25)
        self.win.resolution_selection.add_attribute(cell, 'text', 0)
        self.win.resolution_selection.set_model(self.win.ctrl_store)
        self.win.resolution_selection.connect('changed', self.win.on_resolution_changed)
        self.win.menu_control_box.pack_start(self.win.resolution_selection, False, False, 0)
        self.win.menu_label_box.pack_start(self.win.label, False, False, 0)

    def add_menu_item(self, setting, action):
        self.win.ctrl_combobox = Gtk.ComboBox()
        self.win.ctrl_combobox.set_size_request(-1, 35)
        self.win.ctrl_store = Gtk.ListStore(str)
        cell = Gtk.CellRendererText()
        self.win.ctrl_combobox.pack_start(cell, 25)
        self.win.ctrl_combobox.add_attribute(cell, 'text', 0)
        self.win.ctrl_combobox.set_model(self.win.ctrl_store)
        self.win.ctrl_combobox.connect('changed', action, setting)
        self.win.menu_control_box.pack_start(self.win.ctrl_combobox, False, False, 0)

    def add_int_item(self, line, setting, value, action):
        upper = line.split("max=", 1)[1]
        upper = int(upper.split(' ', 1)[0])
        lower = line.split("min=", 1)[1]
        lower = int(lower.split(' ', 1)[0])
        step = line.split("step=", 1)[1]
        step = int(step.split(' ', 1)[0])
        adj = Gtk.Adjustment(value = value, lower = lower, upper = upper, step_increment = step, page_increment = 1, page_size=0)
        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
        scale.set_digits(0)
        scale.set_value_pos(Gtk.PositionType.RIGHT)
        scale.set_size_request(-1, 35)
        scale.connect("value-changed", action, setting)
        self.win.int_control_box.pack_start(scale, False, False, 0)

    def add_bool_item(self, setting, value, action):
        switch = Gtk.Switch(hexpand = False, vexpand = False)
        if value == 1:
            switch.set_active(True)
        else:
            switch.set_active(False)
        switch.connect ("notify::active", action, setting)
        switch.set_size_request(-1, 25)
        self.win.bool_control_box.pack_start(switch, False, False, 0)
        switch.set_halign(Gtk.Align.START)
        switch.set_valign(Gtk.Align.CENTER)