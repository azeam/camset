import os
import cv2
import subprocess

class Helpers:     
    def get_config_path(self):
        path = "~/.config/camset"
        return os.path.expanduser(path)
    
    def get_active_card(self, win):
        return win.device_selection.get_model()[win.device_selection.get_active()][0]

    def get_video_resolution(self, win):
        text = win.resolution_selection.get_model()[win.resolution_selection.get_active()]
        resolution = text[0].split(" ")[-1]
        pixelformat = text[0].split(" - ", 1)[0]
        vfeedwidth = resolution.split("x", 1)[0]
        vfeedheight = resolution.split("x", 1)[1]
        fourcode = cv2.VideoWriter_fourcc(*'{}'.format(pixelformat))
        return [pixelformat, vfeedwidth, vfeedheight, fourcode]

    def get_card_name(self, card):
        try:
            devnameread = subprocess.run(['v4l2-ctl', '-d', card, '-D'], check=True, universal_newlines=True, stdout=subprocess.PIPE)
            devnameline = devnameread.stdout.split('\n')
            for line in devnameline:
                if "Card type" in line:
                    return line.split(': ', 1)[1].strip()
        except:
            pass