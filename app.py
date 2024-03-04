import cv2 as cv
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from datetime import datetime

REC_HEIGHT = 840
REC_WIDTH = 640
# REC_FPS = 20

picam = Picamera2()
cv.namedWindow("PiCam Feed")

recording = False

config = picam.create_video_configuration(
    main={"size": (REC_HEIGHT, REC_WIDTH)},
)
picam.configure(config)

encoder = JpegEncoder(q=100)

picam.start()

while True:
    frame = picam.capture_array()
    frame_overlay = frame.copy()

    key = cv.waitKey(1)

    if key == ord('e'):
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
            picam.stop()
            break

    if key == ord('r'):
        if recording:
            recording = False
        else:
            recording = True
            recording_start = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            filename = "recording_" + recording_start + ".mjpg"
            print("Started recording to:", filename)
            picam.start_recording(
                encoder=encoder,
                output=filename,
            )

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

    cv.imshow("PiCam Feed", frame_overlay)

cv.destroyAllWindows()
