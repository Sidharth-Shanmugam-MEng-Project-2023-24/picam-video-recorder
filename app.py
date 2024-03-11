import cv2 as cv
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from datetime import datetime

# Width and height of the recording
REC_WIDTH = 840
REC_HEIGHT = 640

# Width, height of the framebuffer
FB_WIDTH = 1920
FB_HEIGHT = 1080
FB_DEPTH = 16

# initialise picam2
picam = Picamera2()

# configure picam2
config = picam.create_video_configuration(
    main={"size": (REC_WIDTH, REC_HEIGHT)},
)
picam.configure(config)

# window to display recording feed (view from X11)
cv.namedWindow("PiCam Feed")

# some status variables
recording = False
light = False

# initialise framebuffer outputs
project_off = np.full(
    (FB_HEIGHT, FB_WIDTH),  # fill into array of this size
    0,                      # fill array with this value (black/off = 0)
    dtype=np.uint16
).reshape(-1)               # flatten to 1d array for writing to framebuffer
project_on = np.full(
    (FB_HEIGHT, FB_WIDTH),  # fill into array of this size
    (2 ** FB_DEPTH - 1),    # Maximum value for given colour depth (white)
    dtype=np.uint16
).reshape(-1)               # flatten to 1d array for writing to framebuffer

# project zeros (black) to the framebuffer to reset output
with open('/dev/fb0', 'wb') as buf:
    buf.write(project_off.tobytes())

# initialise JPEG encoder with quality = 100
encoder = JpegEncoder(q=100)

# start the picam
picam.start()

while True:
    # capture a frame from the picam
    frame = picam.capture_array()
    # clone to overlay text
    frame_overlay = frame.copy()

    # detect a key press
    key = cv.waitKey(1)

    # exit if 'e' key is pressed
    if key == ord('e'):
        # refuse to exit if a video is being recorded
        if recording:
            frame_overlay = cv.putText(
                img=frame_overlay,
                text="     CANNOT EXIT: REC IN PROGRESS!",
                org=(10, 50),
                fontFace=cv.FONT_HERSHEY_SIMPLEX,
                fontScale=1,
                color=(0,0,255),
                thickness=2,
                lineType=cv.LINE_AA
            )
        else:
            # stop the picam
            picam.stop()
            # break out of while loop
            break

    # toggle recording if 'r' pressed
    if key == ord('r'):
        if recording:
            recording = False
        else:
            recording = True
            recording_start = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            filename = "recording_" + recording_start + ".mjpg"
            print("Started recording to:", filename)
            # use picam recording function with the right encoder
            picam.start_recording(
                encoder=encoder,
                output=filename,
            )

    # toggle light when 'l' pressed
    if key == ord('l'):
        if light:
            # turn off light if already on
            light = False
            with open('/dev/fb0', 'wb') as buf:
                buf.write(project_off.tobytes())
        else:
            # turn on light if already off
            light = True
            with open('/dev/fb0', 'wb') as buf:
                buf.write(project_on.tobytes())

    # add text overlay to gui frame if recording
    if recording:
        frame_overlay = cv.putText(
            img=frame_overlay,
            text="REC",
            org=(10, 50),
            fontFace=cv.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255,0,0),
            thickness=2,
            lineType=cv.LINE_AA
        )

    # show the GUI frame
    cv.imshow("PiCam Feed", frame_overlay)

# when exiting, destroy all GUI windows
cv.destroyAllWindows()

# when exiting, reset framebuffer with zero array
with open('/dev/fb0', 'wb') as buf:
    buf.write(project_off.tobytes())
