# Camset
**GUI for v4l2-ctl**

![Screenshot](http://bufonaturvard.se/pics/camset3.png)

**Description**  
This is a tool for easy GUI adjustments of the Video4Linux (V4L) settings on Linux, using v4l2-ctl as backend. All controls are dynamically generated and the application should work with any V4L device, but has only been tested with webcams. The settings applied will remain active when using the webcam in other applications, for example Skype.

The `example_ioctl` folder contains some examples of direct ioctl calls for reading and setting V4L values (equivalent to `v4l2-ctl --list-formats-ext`, `v4l2-ctl -L` and `v4l2-ctl -c`), using the v4l2 Python bindnings library. The library has been slightly modified for compatibility with more recent Python versions (tested with 3.8.2) and is included. 

**Note**  
The application is WIP in early development, but in a functional state. Testing, issue reporting and suggestions are welcome. Do note that there are other applications that are similar and with more functionality (at least for now). This is just a small project to practice some Python.

**Dependencies**  
Python 3  
pip  
v4l2-ctl  
pkg-config

If running from source (not using the camset pip package) you will also need gi (PyGObject @ pip) and OpenCV (opencv-python @ pip)

**Installation**  
For Ubuntu:  
1. `sudo apt-get install python3 python3-pip v4l-utils pkg-config libcairo2-dev libgirepository1.0-dev`  
2. `pip3 install camset`

The pip install includes a .desktop file, which should be picked up by the DE. If `camset` is not found you may need to set up your path environment, for example:  
`PATH=$PATH:/home/USER/.local/bin`
