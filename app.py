"""
Records video from a Raspberry Pi Camera.


"""
import io
import os
import subprocess
import cv2 as cv
from picamera2 import Picamera2
from picamera2.encoders import Encoder
from picamera2.outputs import FileOutput
from datetime import datetime


# Recording parameters
REC_FPS = 30            # Max available framerate is 60 FPS
# REC_RES = (364, 272)    # set to quarter of full sensor resolution
REC_RES = (728, 544)    # set to half of full sensor resolution
# REC_RES = (1456, 1088)    # set full sensor resolution


if __name__ == "__main__":
    # Initialise Pi camera instance
    picam2 = Picamera2()

    # Pi camera configuration:
    picam2.video_configuration.size = REC_RES   # Capture video at defined resolution/size
    picam2.video_configuration.controls.FrameRate = REC_FPS # Capture video at defined framerate
    picam2.video_configuration.encode = 'main'  # Use 'main' stream for encoder
    picam2.video_configuration.format = 'BGR888'    # Use this format for OpenCV compatibility
    picam2.video_configuration.align()          # Align stream size (THIS CHANGES THE RES SLIGHTLY!)

    # Apply the configuration to the Pi camera
    picam2.configure("video")
    
    # Print camera configurations to confirm correct set up
    print(picam2.camera_configuration()['sensor'])
    print(picam2.camera_configuration()['main'])
    print(picam2.camera_configuration()['controls'])

    # Start the Pi camera
    picam2.start()

    # Create CV2 windows
    cv.namedWindow("Pi Camera Feed")

    # Runtime status variables:
    is_recording = False
    is_paused = False

    # Initialise a 'null' encoder to record without any encoding
    recording_encoder = Encoder()

    # Initialise variable to store recording filename and timestamps
    recording_filename = ""
    recording_start_ts = None
    recording_stop_ts = None
    
    while True:
        # Retrieve a frame from the Pi camera for the preview window
        frame_preview = picam2.capture_array("main")

        # Display image to window
        cv.imshow("Pi Camera Feed", frame_preview)

        # Read key press
        keypress = cv.waitKey(1)

        # Pause the preview when 'p' key is pressed - must not be recording
        if (keypress == ord('p')) and not is_recording:
            # If not already paused, then pause
            if not is_paused:
                # Set paused status
                is_paused = True

                # Keep polling to check for unpause request
                while is_paused:
                    # Read keypress
                    keypress = cv.waitKey(1)

                    # if 'p' pressed, unpause
                    if keypress == ord('r'):
                        # Reset the pause status
                        is_paused = False

                        # Break out of the pause loop
                        break
                    else:
                        # Do nothing if any other key was pressed
                        pass


        # Toggle recording when 'r' key is pressed
        if keypress == ord('r'):
            # If not already recording, start recording
            if not is_recording:
                # Set the recording status to true
                is_recording = True

                # Initialise a memory buffer to store video recording
                recording_membuff = io.BytesIO()
                recording_output = FileOutput(recording_membuff)

                # Generate starting timestamp
                recording_start_ts = datetime.now()
                recording_start_ts_str = recording_start_ts.strftime("%m-%d-%Y-%H-%M-%S")

                # Generate filename
                recording_filename = "recording_" + recording_start_ts_str

                # Reset recording end timestamp
                recording_stop_ts = None

                # Start the recording
                picam2.start_recording(
                    encoder=recording_encoder,  # Null encoder for 'raw' footage
                    output=recording_output     # Record directly to memory
                )

                # Log to console
                print("Started recording:", recording_filename)

            # If already recording, stop recording
            else:
                # Stop the recording
                picam2.stop_recording()

                # stop_recording() entirely stops the Pi camera with stop()
                picam2.start()

                # Generate stopped timestamp
                recording_stop_ts = datetime.now()
                recording_stop_ts_str = recording_stop_ts.strftime("%m-%d-%Y-%H-%M-%S")

                # Log to console
                print("Stopped recording:"
                    + recording_filename
                    + " (Stopped at: "
                    + recording_stop_ts_str
                    + ")"
                )
                print("Please wait, unloading recording from memory buffer...")

                # Save to file
                with open(recording_filename, "xb") as file:
                    file.write(recording_membuff.getbuffer())

                # Reset recording start timestamp
                recording_start_ts = None

                # Close recording memory buffer to discard data and clear RAM space 
                recording_membuff.close()

                # Generate encoded recording filename
                recording_filename_mkv = recording_filename + ".mkv"

                # Log to console
                print("Please wait, encoding raw recording to lossless mkv...: " + recording_filename_mkv)

                # Get the aligned resolution of the recording
                (aligned_width, aligned_height) = picam2.camera_configuration()['main']['size']

                # FFmpeg command to convert video from BGR888 to MKV (lossless FFV1 codec)
                ffmpeg_command = [
                    'ffmpeg',                                   # call FFmpeg
                    '-f', 'rawvideo',                           # force raw data type
                    '-s', f'{aligned_width}x{aligned_height}',  # width and height
                    '-pix_fmt', 'bgr24',                        # set BGR888 format
                    '-i', recording_filename,                   # filename of raw file
                    '-c:v', 'ffv1',                             # lossless FFV1 codec
                    '-y',                                       # overwrite output file if exists
                    '-loglevel', 'error',                       # only show errors in console
                    '-stats',                                   # show progress stats
                    recording_filename_mkv                      # output filename
                ]

                # Run FFmpeg command as a subprocess
                subprocess.run(ffmpeg_command)

                # Delete raw file
                os.remove(recording_filename)

                # Log to console
                print("Write complete, it is safe to exit or record again: " + recording_filename_mkv)

                # Set the recording status to false to allow program exiting
                is_recording = False

        # Exit program when 'e' key is pressed
        if keypress == ord('e'):
            # If exiting while recording, alert that recording must be stopped first
            if is_recording:
                # Log to console
                print("Cannot exit, recording or file writing in progress!")
            else:
                # Break out of while to exit cleanly
                break

    # When exiting, destroy all GUI windows
    cv.destroyAllWindows()

    # Once the while loop exits, recording is stopped, so camera must stop too
    picam2.stop()

    # Print to console
    print("Pi Camera has been stopped")

    # Exit
    exit()






"""
[1] https://stackoverflow.com/a/42565861
[2] https://stackoverflow.com/a/51768527
"""
