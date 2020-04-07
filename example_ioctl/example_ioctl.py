import v4l2
import fcntl

# Working example code for direct ioctl calls, should be much faster than all the string splitting, but trickier to work with
# The Python V4L bindings are outdated, some slight modifications have been made for Python3 compatibility 

def read_ioctl_capabalities():
    vd = open('/dev/video0', 'rb+', buffering=0)
    cp = v4l2.v4l2_capability()
    encoding = 'utf-8'
    
    fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCAP, cp)
    print(str(cp.card, encoding))
    print(str(cp.driver, encoding))
    print("video capture device?\t", bool(cp.capabilities & v4l2.V4L2_CAP_VIDEO_CAPTURE))
    print("Supports read() call?\t", bool(cp.capabilities & v4l2.V4L2_CAP_READWRITE))
    print("Supports streaming?\t", bool(cp.capabilities & v4l2.V4L2_CAP_STREAMING))

    fmt = v4l2.v4l2_format()
    fmt.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    fcntl.ioctl(vd, v4l2.VIDIOC_G_FMT, fmt)
    print("Width:", fmt.fmt.pix.width)
    print("Height:", fmt.fmt.pix.height)

    fmtdesc = v4l2.v4l2_fmtdesc()
    fmtdesc.type = v4l2.V4L2_BUF_TYPE_VIDEO_CAPTURE
    fmtdesc.index = 0 # possible to get 0 and 1 (default for each codec), how to read other resolution options?
    fcntl.ioctl(vd, v4l2.VIDIOC_ENUM_FMT, fmtdesc)
    print("Resolution:", str(fmtdesc.description, encoding))

    qctrl = v4l2.v4l2_queryctrl()
    mctrl = v4l2.v4l2_querymenu()
    vctrl = v4l2.v4l2_control()
    qctrl.id = v4l2.V4L2_CID_BASE; 
    mctrl.index = 0
    
    # does not include the exposure auto menu, which v4l2-ctl shows, even if changed to V4L2_CID_CAMERA_CLASS_BASE, not sure why
    while qctrl.id < v4l2.V4L2_CID_LASTP1: 
        try:
            vctrl.id = qctrl.id
            fcntl.ioctl(vd, v4l2.VIDIOC_QUERYCTRL, qctrl)
            fcntl.ioctl(vd, v4l2.VIDIOC_G_CTRL, vctrl)
            print(str(qctrl.name, encoding))
            print(qctrl.type)
            print(qctrl.maximum)
            print(qctrl.minimum)
            print(vctrl.value)
            '''
            win.label = Gtk.Label(hexpand = True, vexpand = False)
            win.label.set_text(str(qctrl.name, encoding))
            win.label.set_size_request(-1, 35)
            win.label.set_halign(Gtk.Align.END)
            adj = Gtk.Adjustment(value = vctrl.value, lower = qctrl.minimum, upper = qctrl.maximum, step_increment = qctrl.step, page_increment = 5, page_size=0)
            win.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
            win.scale.set_digits(0)
            win.scale.set_value_pos(Gtk.PositionType.RIGHT)
            win.scale.set_size_request(-1, 35)
            win.scale.connect("value-changed", set_int_value, "dev", "setting")
            win.intcontrolbox.pack_start(win.scale, False, False, 0)
            win.intlabelbox.pack_start(win.label, False, False, 0)
            '''
            if qctrl.type == 3: # is menu
                while mctrl.index <= qctrl.maximum:
                    mctrl.id = qctrl.id
                    fcntl.ioctl(vd, v4l2.VIDIOC_QUERYMENU, mctrl)
                    print(str(qctrl.name, encoding))
                    print(str(mctrl.name, encoding))
                    print(mctrl.index)
                    mctrl.index += 1
        except:
            pass
        qctrl.id += 1
    vd.close()

def main():
    read_ioctl_capabalities()

if __name__ == "__main__":
    main()