""" Records video from a Raspberry Pi Camera. """

import matplotlib.pyplot as plt
import cv2

from ProjectorManager import Projector
from CameraManager import Camera
from PreviewManager import Preview

# Recording parameters
REC_FPS = 30            # Max available framerate is 60 FPS
REC_WIDTH = 728         # Set to half of full sensor width
REC_HEIGHT = 544        # Set to half of full sensor height
REC_CROP_HEIGHT = (None, None)
REC_CROP_WIDTH = (None, None)
# REC_CROP_HEIGHT = (0, 320)
# REC_CROP_WIDTH = (430, 700)

# Framebuffer parameters
FB_WIDTH = 1280
FB_HEIGHT = 800
FB_DEPTH = 16

if __name__ == "__main__":
    # Create preview window instance
    preview = Preview()

    # Initialise framebuffer - reset fb with light source off
    light = Projector(FB_WIDTH, FB_HEIGHT, FB_DEPTH, False)

    # Initialise Pi camera
    camera = Camera(REC_WIDTH, REC_HEIGHT, REC_FPS, REC_CROP_WIDTH, REC_CROP_HEIGHT)

    # Calibrate mode
    calibration_status = ""
    
    # This is the main runtime loop
    while True:
        # capture a frame
        frame = camera.captureFrame()

        # Retrieve a frame from the Pi camera for the preview window
        preview.showFrame(
            frame,
            calibration_status,
            camera.getStatus(),
            light.getStatus()
        )

        # Read key press
        keypress = preview.getKeypress()

        # Toggle light when 'l' key is pressed
        if keypress == ord('l'):
            light.toggle()


        # Toggle recording when 'r' key is pressed
        if keypress == ord('r'):
            camera.toggleRecording()


        # Exit program when 'e' key is pressed
        if keypress == ord('e'):
            # Send shutdown request to camera instance
            camera.shutdown()

            # When exiting, reset framebuffer with zero array
            light.off()

            # Send shutdown request to preview instance
            preview.shutdown()

            # Exit
            break

        # Measure mode when 'm' key is pressed
        if keypress == ord('m'):
            light.off()
            plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), origin='upper')
            plt.show()
    
    # Exit from the script
    exit()
