import cv2
from picamera2 import Picamera2

piCam = Picamera2()
piCam.preview_configuration.main.size=(1280, 960)
piCam.preview_configuration.main.format="RGB888"
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()

# USB Cam
# cam = cv2.VideoCapture('/dev/video0')
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Width
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Height

def generateFrames():
    while True:
        # USB Cam
        # 
        # success, frame = cam.read()
        # if not success:
        #     print("Failed to capture image!")
        #     break
        
        # print("Frame captured successfully")  
        
        frame = piCam.capture_array()

        frame = cv2.rotate(frame, cv2.ROTATE_180)
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            print("Failed to encode frame")
            break

        frame = buffer.tobytes()
        
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
if __name__ == "__main__":
    generateFrames()