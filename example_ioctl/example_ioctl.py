import v4l2
import fcntl

# Working example code for direct ioctl calls, should be much faster than all the subprocesses and string splitting, but trickier to work with
#
# Tried implementing this but there's barely any performance difference from what I can tell, nor much difference in code quantity.
# Startup lag is probably mainly caused by gtk widgets building. Might continue with the string splitting, uglier but easier
#
# The Python V4L bindings are outdated, some slight modifications have been made for Python 3.8.2 compatibility 

def get_detailed_outputs(vd, pixel_format, width, height):
    qctrl = v4l2.v4l2_frmivalenum()
    qctrl.pixel_format = pixel_format
    qctrl.width = width
    qctrl.height = height
    qctrl.index = 0
    while qctrl.index < 10: # TODO: better loop
        fcntl.ioctl(vd, v4l2.VIDIOC_ENUM_FRAMEINTERVALS, qctrl)
        if qctrl.type == v4l2.V4L2_FRMIVAL_TYPE_DISCRETE: 
            print("Width:", width, "Height:", height, "FPS:", 1.0*qctrl.discrete.denominator/qctrl.discrete.numerator)
        else:
            print(width, height, 1.0*qctrl.stepwise.max.denominator/qctrl.stepwise.max.numerator, 1.0*qctrl.stepwise.min.denominator/qctrl.stepwise.min.numerator)
        qctrl.index += 1    

def get_outputs(pixel_format):
    vd = open('/dev/video0', 'rb+', buffering=0)
    
    qctrl = v4l2.v4l2_frmsizeenum()
    qctrl.type = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
    qctrl.index = 0
    qctrl.pixel_format = pixel_format

    while qctrl.index < 10: # TODO: better loop
        try:
            fcntl.ioctl(vd, v4l2.VIDIOC_ENUM_FRAMESIZES, qctrl)
            if (qctrl.type == v4l2.V4L2_FRMSIZE_TYPE_DISCRETE):
                get_detailed_outputs(vd, qctrl.pixel_format, qctrl.discrete.width, qctrl.discrete.height)
            else:
                # TODO: translate to Python, can't test because no device with stepsize
                ''' 
                for (width=frmsize.stepwise.min_width; width< frmsize.stepwise.max_width; width+=frmsize.stepwise.step_width)
                    for (height=frmsize.stepwise.min_height; height< frmsize.stepwise.max_height; height+=frmsize.stepwise.step_height)
                        printFrameInterval(fd, frmsize.pixel_format, width, height);
                '''
        except:
            pass
        qctrl.index += 1
    vd.close()

def read_camera_controls(): # CID_BASE IDs do not include all settings that v4l2-ctl -L has, check CAMERA_CLASS_BASE ID range for the rest
    vd = open('/dev/video0', 'rb+', buffering=0)
    encoding = 'utf-8'
    qctrl = v4l2.v4l2_queryctrl()
    mctrl = v4l2.v4l2_querymenu()
    vctrl = v4l2.v4l2_control()
    qctrl.id = v4l2.V4L2_CID_CAMERA_CLASS_BASE
    mctrl.index = 0
    
    while qctrl.id < v4l2.V4L2_CID_PRIVACY:
        try:
            vctrl.id = qctrl.id
            fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCTRL, qctrl)
            fcntl.ioctl(vd, v4l2.VIDIOC_G_CTRL, vctrl)
            print("Control name:", str(qctrl.name, encoding))
            print("Control type, 1=int, 2=bool, 3=menu:", qctrl.type) 
            
            print("Maximum:", qctrl.maximum)
            print("Minimum:", qctrl.minimum)
            print("Step:", qctrl.step)
            print("Default:", qctrl.default_value)
            print("Value:", vctrl.value)
            
            if qctrl.type == 3: # is menu
                while mctrl.index <= qctrl.maximum:
                    try: # needed because sometimes index 0 doesn't exist but 1 does
                        mctrl.id = qctrl.id
                        fcntl.ioctl(vd, v4l2.VIDIOC_QUERYMENU, mctrl)
                        print("Menu name:", str(qctrl.name, encoding))
                        print("Menu option name:", str(mctrl.name, encoding))
                        print("Menu option index:", mctrl.index)
                        mctrl.index += 1
                    except:
                        mctrl.index += 1
                
        except:
            pass
        qctrl.id += 1
    vd.close()

def set_value(controlid):
    vd = open('/dev/video0', 'rb+', buffering=0)
    vctrl = v4l2.v4l2_control()
    vctrl.id = controlid
    vctrl.value = 0 # testing with 0, should read from widget
    fcntl.ioctl(vd, v4l2.VIDIOC_S_CTRL, vctrl)

def read_base_capabalities():
    vd = open('/dev/video0', 'rb+', buffering=0)
    cp = v4l2.v4l2_capability()
    encoding = 'utf-8'
    
    # basic info
    fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)
    print(str(cp.card, encoding))
    print(str(cp.driver, encoding))
    print("video capture device?\t", bool(cp.capabilities & v4l2.V4L2_CAP_VIDEO_CAPTURE))
    print("Supports read() call?\t", bool(cp.capabilities & v4l2.V4L2_CAP_READWRITE))
    print("Supports streaming?\t", bool(cp.capabilities & v4l2.V4L2_CAP_STREAMING))

    # current height, width
    qctrl = v4l2.v4l2_format()
    qctrl.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    fcntl.ioctl(vd, v4l2.VIDIOC_G_FMT, qctrl)
    print("Width:", qctrl.fmt.pix.width)
    print("Height:", qctrl.fmt.pix.height)

    # output overview
    qctrl = v4l2.v4l2_fmtdesc()
    qctrl.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    qctrl.index = 0
    fcntl.ioctl(vd, v4l2.VIDIOC_ENUM_FMT, qctrl)
    print("Format:", str(qctrl.description, encoding))
    print("Pixelformat ID:", qctrl.pixelformat)
    get_outputs(qctrl.pixelformat) # pass pixelformat to read outputs, increase index for different codecs

    # main controls
    qctrl = v4l2.v4l2_queryctrl()
    mctrl = v4l2.v4l2_querymenu()
    vctrl = v4l2.v4l2_control()
    qctrl.id = v4l2.V4L2_CID_BASE
    mctrl.index = 0
    
    while qctrl.id < v4l2.V4L2_CID_LASTP1: # LASTP1 is last item in CID_BASE
        try:
            vctrl.id = qctrl.id
            fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCTRL, qctrl)
            fcntl.ioctl(vd, v4l2.VIDIOC_G_CTRL, vctrl)
            print("Control name:", str(qctrl.name, encoding))
            print("Control type, 1=int, 2=bool, 3=menu:", qctrl.type) 
            '''
            There are more types, 4=BUTTON, 5=INTEGER64, 6=CTRL_CLASS, 7=STRING, 8=BITMASK,	9=INTEGER_MENU
            Not sure what to do with those, can't test
            '''
            print("Maximum:", qctrl.maximum)
            print("Minimum:", qctrl.minimum)
            print("Step:", qctrl.step)
            print("Default:", qctrl.default_value)
            print("Value:", vctrl.value)
            set_value(vctrl.id) # test setting value
            '''
            if qctrl.type == 1: # int
                win.label = Gtk.Label(hexpand = True, vexpand = False)
                win.label.set_text(str(qctrl.name, encoding))
                win.label.set_size_request(-1, 35)
                win.label.set_halign(Gtk.Align.END)
                adj = Gtk.Adjustment(value = vctrl.value, lower = qctrl.minimum, upper = qctrl.maximum, step_increment = qctrl.step, page_increment = 5, page_size=0)
                win.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
                win.scale.set_digits(0)
                win.scale.set_value_pos(Gtk.PositionType.RIGHT)
                win.scale.set_size_request(-1, 35)
                win.scale.connect("value-changed", set_int_value, card, vctrl.id)
                win.intcontrolbox.pack_start(win.scale, False, False, 0)
                win.intlabelbox.pack_start(win.label, False, False, 0)
            '''
            if qctrl.type == 3: # is menu
                while mctrl.index <= qctrl.maximum:
                    try:
                        mctrl.id = qctrl.id
                        fcntl.ioctl(vd, v4l2.VIDIOC_QUERYMENU, mctrl)
                        print("Menu name:", str(qctrl.name, encoding))
                        print("Menu option name:", str(mctrl.name, encoding))
                        print("Menu option index:", mctrl.index)
                        mctrl.index += 1
                    except:
                        mctrl.index += 1
        except:
            pass
        qctrl.id += 1
    vd.close()

def main():
    read_base_capabalities()
    read_camera_controls()

if __name__ == "__main__":
    main()