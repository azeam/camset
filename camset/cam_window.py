import cv2
import gi
import subprocess

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, GLib, Gtk

class CamWindow(Gtk.Window):
    def __init__(self, win, dialogs):
        self.win = win
        self.dialogs = dialogs
        self.videosize = 100
        self.cap = None
        self.run_id = 0

        Gtk.Window.__init__(self, title="Camera feed")
        self.connect('delete-event', lambda w, e: self.stop_camera_feed() or True) # override delete and just hide window, or widgets will be destroyed
        videoframe = self.setup_video()
        self.setup_video_controls(videoframe)

    def stop_camera_feed(self):
        self.cap = None
        self.hide()
        self.win.btn_showcam.set_active(False)
        if self.run_id > 0:
            GLib.source_remove(self.run_id)
        self.run_id = 0

    def setup_video(self):
        fixed = Gtk.Fixed()
        self.add(fixed)
        self.image_area = Gtk.Box() 
        self.videobox = Gtk.Box(spacing=10, orientation=Gtk.Orientation.VERTICAL)
        self.image = Gtk.Image()
        self.videobox.add(self.image_area)
        self.image_area.add(self.image)
        self.image_area.show_all()
        return fixed

    def setup_video_controls(self, fixed):
        self.vidcontrolgrid = Gtk.Grid()
        self.vidcontrolgrid.set_column_homogeneous(True)
        self.label = Gtk.Label(label="Camera feed scale (percentage)")  
        self.adj = Gtk.Adjustment(value = self.videosize, lower = 1, upper = 100, step_increment = 1, page_increment = 1, page_size=0)
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=self.adj)
        self.scale.set_digits(0)
        self.scale.set_value_pos(Gtk.PositionType.RIGHT)
        self.scale.set_margin_end(20)
        self.scale.connect("value-changed", self.set_video_size)
        self.vidcontrolgrid.add(self.label)
        self.vidcontrolgrid.add(self.scale)
        fixed.put(self.vidcontrolgrid, 30, 30)
        fixed.put(self.videobox, 0, 90)
        self.show_all()

    def set_video_size(self, callback):
        self.videosize = callback.get_value()

    def show_frame(self):
        if self.cap is None:
            return False
        ret, frame = self.cap.read()
        if frame is not None:
            width = int(frame.shape[1] * self.videosize / 100)
            height = int(frame.shape[0] * self.videosize / 100)
            dim = (width, height)
            # TODO: resizing video and window this way is very cpu intensive for large resolutions, should be improved or removed
            frame = cv2.resize(frame, dim, interpolation = cv2.INTER_CUBIC)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # needed for proper color representation in gtk
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(frame.tostring(),
                                                GdkPixbuf.Colorspace.RGB,
                                                False,
                                                8,
                                                frame.shape[1],
                                                frame.shape[0],
                                                frame.shape[2]*frame.shape[1]) # last argument is "rowstride (int) - Distance in bytes between row starts" (??)
            self.image.set_from_pixbuf(pixbuf.copy())
        self.resize(1, 1)
        return True

    def start_camera_feed(self, pixelformat, vfeedwidth, vfeedheight, fourcode):
        card = self.win.card
    
        process = subprocess.Popen(['v4l2-ctl', '-d', card, '-v', 'height={0},width={1},pixelformat={2}'.format(vfeedheight, vfeedwidth, pixelformat)], universal_newlines=True, stdout=subprocess.PIPE)
        out, err = process.communicate()
        if process.returncode == 0:
            cap = cv2.VideoCapture(card, cv2.CAP_V4L2)
            # also set resolution to cap, otherwise cv2 will use default and not the res set by v4l2
            cap.set(3,int(vfeedwidth))
            cap.set(4,int(vfeedheight))
            cap.set(cv2.CAP_PROP_FOURCC, fourcode)
            # cap.set(5,1) 1 fps
            self.cap = cap
            return GLib.idle_add(self.show_frame) 
        else: 
            if "Device or resource busy" in str(out):
                errorMsg = "Unable to start feed, the device is busy"
            elif process.returncode == 1:
                errorMsg = "Unable to start feed, not a valid output device"
            else:
                errorMsg = "Unable to start feed, unknown error"
            self.dialogs.show_message(errorMsg, True, self.win)
        return 0

    def init_camera_feed(self, list):
        self.run_id = self.start_camera_feed(list[0], list[1], list[2], list[3])
        if self.run_id > 0:
            self.win.btn_showcam.set_active(True)
            self.show()
        else:
            self.stop_camera_feed()