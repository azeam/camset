# Camset
**GUI for v4l2-ctl**

![Screenshot](http://bufonaturvard.se/pics/camset2.png)

**Description**  
This is a tool for easy GUI adjustments of the Video4Linux (V4L) settings on Linux, using v4l2-ctl as backend. All controls are dynamically generated and the application should work with any other V4L device, but has only been tested with webcams. The changes will remain active when using the webcam in other applications, for example Skype.

**Note**  
The application is WIP but in a functional state. Testing, issue reporting and suggestions are welcome. 

**Dependencies**  
Python 3.7+  
pip  
v4l2-ctl  
pkg-config

If running from source (not using the camset pip package) you will also need gi (PyGObject @ pip) and OpenCV (opencv-python @ pip)

**Installation**  
For Ubuntu:  
1. `sudo apt-get install python3 python3-pip v4l-utils pkg-config`  
2. `pip3 install camset`

The pip install includes a .desktop file, which should be picked up by the DE. If `camset` is not found you may need to set up your path environment, for example:  
`$PATH=$PATH:/home/USER/.local/bin`