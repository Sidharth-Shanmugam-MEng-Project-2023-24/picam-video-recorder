# webcam-video-recorder
Python script to record video from a Raspberry Pi Camera stream to a file, simultaneously driving a projector light source using the Framebuffer.

The aim of this software is to record test footage of bubbles from the underwater testing facility at the [Institute for Safe Autonomy](https://www.york.ac.uk/safe-autonomy/). The software drives a DLP projector, connected via HDMI and using the Framebuffer to eliminate the need for a desktop environment, to power a toggle-able light source. Footage is recorded from a Raspberry Pi Global Shutter camera.

## Prerequisites
1. Connect GS camera to Pi using the MIPI interface.
2. Connect DLP projector to either of the Pi's HDMI ports.
3. Connect Pi to Desktop/Laptop via Ethernet.
4. SSH into Pi with X11 forwarding (`ssh -X sid@sidpi4.local`).

## Usage
The [Picamera2](https://github.com/raspberrypi/picamera2) library, although only available as a beta release at the time of writing, is a Python interface to provide high-level access to the Raspberry Pi Cameras and Pi computer's built-in imaging hardware. [OpenCV](https://opencv.org) is a computer vision library which provides a simple-to-use, high-level GUI framework.

This Python script utilises the Picamera2 library to initialise the attached Raspberry Pi Global Shutter camera with recording parameters, then, in an infinite while-loop, captures a frame from the GS camera to display as a preview to a window using OpenCV, with text-based status message overlays. Recording footage is possible using the record function and a video encoder implementation from the Picamera2 library.

### Parameters 1: Recording resolution
The resolution to record in is controlled by the `REC_WIDTH` and `REC_HEIGHT` constants. By default: `REC_WIDTH=840` and `REC_HEIGHT=640`.

The values stored in this constant is passed to Picamera2's `create_video_configuration()` and `configure()` functions, which initialises the GS camera for video recording.

### Parameters 2: Framebuffer size
Since different HDMI outputs can use different resolutions, use the `fbset -fb /dev/fb0` command to retrive the Framebuffer parameters, you should see something like this as an output:

```
sid@sidpi4:~ $ fbset -fb /dev/fb0

mode "1920x1080"
    geometry 1920 1080 1920 1080 16
    timings 0 0 0 0 0 0 0
    rgba 5/11,6/5,5/0,0/0
endmode
```

Ensure the `FB_HEIGHT` and `FB_WIDTH` constants match the resolution shown in the command output (`mode "1920x1080"`). Next, ensure the `FB_DEPTH` contant matches the depth shown from the command output (last number in the line: `geometry 1920 1080 1920 1080 16`).

### Starting the script and controls
Run the script with `python app.py`.

The `l` key toggles the light source: when the light is toggled on, the script writes an array of the value for 'white' to the Framebuffer. When the light is toggled off, the script writes an array of 'black'.

The `r` key toggles the recording: press to start the recording, and again to end the recording. The file is saved in the format: `recording_%m-%d-%Y-%H-%M-%S.mjpg`.

The `e` key exits the script as long as it isn't recording, otherwise, the recording must be stopped with the `r` key before the `e` key has any effect.

### Moving the recording file to another computer
I've been using the secure copy protocol (SCP) to copy the recording files from the Pi to my personal machine.

From the Pi, after cd'ing to the directory with the recording:

```
scp recording_<RECORDING_TIMESTAMP>.mjpg <USER>@<RECIPIENT_IP>:/<PATH>
```

For example:

```
scp recording_03-05-2024-14-39-33.mjpg sid@192.168.0.1:/Users/sid/Desktop
```

Note: You must have a running SSH daemon/service on the recipient computer.

## Bugs and WIP
### Bug: Program fails to launch: no Qt platform plugin could be initialized
Occasionally, when launching the script, you may result in this error message:

```
sid@sidpi4:~/picam-video-recorder $ python app.py 
[2:41:37.021666797] [3809]  INFO Camera camera_manager.cpp:284 libcamera v0.2.0+46-075b54d5
[2:41:37.061594176] [3847]  WARN RPiSdn sdn.cpp:39 Using legacy SDN tuning - please consider moving SDN inside rpi.denoise
[2:41:37.063347788] [3847]  INFO RPI vc4.cpp:447 Registered camera /base/soc/i2c0mux/i2c@1/imx296@1a to Unicam device /dev/media4 and ISP device /dev/media0
[2:41:37.063407342] [3847]  INFO RPI pipeline_base.cpp:1144 Using configuration file '/usr/share/libcamera/pipeline/rpi/vc4/rpi_apps.yaml'
[2:41:37.066034084] [3809]  INFO Camera camera_manager.cpp:284 libcamera v0.2.0+46-075b54d5
[2:41:37.089617559] [3850]  WARN RPiSdn sdn.cpp:39 Using legacy SDN tuning - please consider moving SDN inside rpi.denoise
[2:41:37.091225119] [3850]  INFO RPI vc4.cpp:447 Registered camera /base/soc/i2c0mux/i2c@1/imx296@1a to Unicam device /dev/media4 and ISP device /dev/media0
[2:41:37.091326543] [3850]  INFO RPI pipeline_base.cpp:1144 Using configuration file '/usr/share/libcamera/pipeline/rpi/vc4/rpi_apps.yaml'
[2:41:37.097325085] [3809]  INFO Camera camera.cpp:1183 configuring streams: (0) 840x640-XBGR8888 (1) 1456x1088-SBGGR10_CSI2P
[2:41:37.097725151] [3850]  INFO RPI vc4.cpp:611 Sensor: /base/soc/i2c0mux/i2c@1/imx296@1a - Selected sensor format: 1456x1088-SBGGR10_1X10 - Selected unicam format: 1456x1088-pBAA
qt.qpa.xcb: could not connect to display localhost:10.0
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "/home/sid/.local/lib/python3.11/site-packages/cv2/qt/plugins" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: xcb.

Aborted
```
I'm not exactly sure what is causing this, and I haven't had any time to debug it. However, a simple fix is to log out, then log back in, after which the program should launch perfectly.

### WIP: Recording footage in raw format
An earlier commit of `app.py` had a *working* implementation of raw format video recording. The script was generating a .raw file, which, however, I was unable to figure out how to open. I understand this is a binary file but I am unsure as to how the file is formatted. I will be researching how to parse this raw format and will later re-implement this feature.

For now, I've fallen back to a fully-working solution with the `JpegEncoder` and quality set to 100. The output file, although unable to open in VLC or QuickTime, does open in [mpv](https://mpv.io).
