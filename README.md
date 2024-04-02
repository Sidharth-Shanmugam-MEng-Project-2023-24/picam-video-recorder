# picam-video-recorder
Python script to record video from a Raspberry Pi Camera stream to a file, simultaneously driving a projector light source using the Framebuffer

This software aims to record test footage of bubbles from the underwater testing facility at the [Institute for Safe Autonomy](https://www.york.ac.uk/safe-autonomy/) using a Raspberry Pi 4/5 and a Pi Global Shutter Camera. The software also drives a DLP projector, connected via HDMI and using the Framebuffer to eliminate the need for a desktop environment, to power a toggle-able light source.

## Prerequisites
1. Connect the GS camera to Pi using the MIPI interface.
2. Connect the DLP projector to Pi's HDMI ports.
3. Connect Pi to Desktop/Laptop via Ethernet.
4. SSH into Pi with X11 forwarding (e.g., `ssh -X sid@sidpi4.local`).

## Usage
The [Picamera2](https://github.com/raspberrypi/picamera2) library, although only available as a beta release at the time of writing, is a Python interface to provide high-level access to the Raspberry Pi Cameras and Pi computer's built-in imaging hardware. [OpenCV](https://opencv.org) is a computer vision library which provides a simple-to-use, high-level GUI framework.

This Python script utilises the Picamera2 library to initialise the attached Raspberry Pi Global Shutter camera with recording parameters, then, in an infinite while-loop, captures a frame from the GS camera to display as a preview to a window using OpenCV, with text-based status message overlays. Recording footage is possible using the record function and a video encoder implementation from the Picamera2 library.

From the Picamera2 documentation, the camera module sends the captured data to the CSI-2 Receiver on-board the Pi, which will buffer the data to memory. At this point, the data is unprocessed and a direct (Bayer) output from the sensor. The 'raw' stream allows for this data to be read, however, vast amounts of pre-processing is required before this data is human-understandable. From the memory module, the data then moves to an 'Image Signal Processor' (ISP) module, again, on-board the Pi, which processes the raw stream into a human parseable, such as BGR888. Unless a specific type of encoding is requested in code, this data stays un-encoded, thus 'raw', and passed to the 'main' stream. A 'lores' stream exists as a low resolution stream, but is not required for this program.

```
Camera Module 
    |--> CSI-2 Rx. 
            |--> Mem 
                  |--> ISP
                  |     |--> 'main' stream
                  |     |--> 'lores' stream
                  |--------> 'raw' stream
```

Since the 'Image Signal Processor' efficiently processes this 'raw' stream into a human-understandable format, this software records the 'main' stream, which is the 'raw' stream converted into BGR888 from the sensor-specific format by the ISP, to a memory buffer. When the recording finishes, the memory buffered data is moved to the disk, then passed into the FFmpeg software to convert into a video file format (MKV) using a lossless encoder (FFV1) so that the output file can be opened by a general-purpose video playback software such as VLC and the file size of the recording is reduced.

### Parameters 1: Recording resolution
The resolution and framerate to record with is controlled by the `REC_WIDTH`, `REC_HEIGHT`, and `REC_FPS` constants. By default: `REC_WIDTH=728`, `REC_HEIGHT=544`, and `REC_FPS=30` which is half of the full resolution and half of the max framerate of the sensor.

The values stored in this constant are passed to Picamera2's `create_video_configuration()` and `configure()` functions, which initialises the GS camera for video recording.

### Parameters 2: Framebuffer size
Since different HDMI outputs can use different resolutions, use the `fbset -fb /dev/fb0` command to retrieve the Framebuffer parameters, you should see something like this as an output:

```
sid@sidpi4:~ $ fbset -fb /dev/fb0

mode "1920x1080"
    geometry 1920 1080 1920 1080 16
    timings 0 0 0 0 0 0 0
    rgba 5/11,6/5,5/0,0/0
endmode
```

Ensure the `FB_HEIGHT` and `FB_WIDTH` constants match the resolution shown in the command output (`mode "1920x1080"`). Next, ensure the `FB_DEPTH` constant matches the depth shown from the command output (the last number in the line is `geometry 1920 1080 1920 1080 16`).

### Starting the script and controls
Run the script with `python app.py`.

The `l` key toggles the light source: when the light is toggled on, the script writes an array of the value for 'white' to the Framebuffer. When the light is toggled off, the script writes an array of 'black'.

The `r` key toggles the recording: press to start the recording, and again to end the recording. The file is saved in the format: `recording_%m-%d-%Y-%H-%M-%S.mkv`.

The `e` key exits the script, if a recording was in progress when this key is pressed, the recording is gracefully stopped and the file is saved.

### Moving the recording file to another computer
I've been using the secure copy protocol (SCP) to copy the recording files from the Pi to my machine.

From the Pi, after cd'ing to the directory with the recording:

```
scp recording_<RECORDING_TIMESTAMP>.mjpg <USER>@<RECIPIENT_IP>:/<PATH>
```

For example:

```
scp recording_03-05-2024-14-39-33.mjpg sid@192.168.0.1:/Users/sid/Desktop
```

Note: You must have an active SSH daemon/service on the recipient's computer.

## Bugs and WIP
### Bug: Program fails to launch: no Qt platform plugin could be initialized
Occasionally, when launching the script, you may encounter this error message:

```
sid@sidpi5:~/picam-video-recorder $ python app.py 
qt.qpa.xcb: could not connect to display localhost:12.0
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.

Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, xcb.

Aborted
```

I'm not exactly sure what is causing this, and I haven't had any time to debug it. However, a simple fix is to log out, then log back in, after which the program should launch perfectly.
