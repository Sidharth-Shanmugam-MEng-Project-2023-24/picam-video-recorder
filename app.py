import cv2 as cv
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from datetime import datetime

REC_HEIGHT = 840
REC_WIDTH = 640
REC_FPS = 20

picam = Picamera2()
cv.namedWindow("PiCam Feed")

recording = False

config = picam.create_video_configuration(
    main={"size": (REC_HEIGHT, REC_WIDTH)}
)
picam.configure(config)
picam.start()

while True:
    frame = picam.capture_array()
    frame_overlay = frame.copy()

    key = cv.waitKey(1)

    if key == ord('e'):
        if recording:
            picam.stop_recording()
        picam.stop()
        break

    if key == ord('r'):
        if recording:
            recording = False
        else:
            recording = True
            recording_start = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
            filename = "recording_" + recording_start + ".h264"
            print("Started recording to:", filename)
            picam.start_recording(
                encoder=H264Encoder(),
                output=filename,
                quality=Quality.VERY_HIGH
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
