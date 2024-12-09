import camThings as cam
import main_functions
import RGB_Strip

from flask_socketio import SocketIO
from flask import Flask
from flask import (
    Response,
    render_template,
    request,
    abort
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'    
socketio = SocketIO(app)


# Default RGB sequence is server address in binary
main_functions.changeRGB(RGB_Strip.displayBinaryText) 

# IP Whitelisting
# ALLOWED_IPS = []
# 
# @app.errorhandler(403)
# def permission_error(e):
#     return render_template('403.html', error_code=403), 403
# 
# @app.before_request
# def limit_remote_addr():
#     client_ip = str(request.remote_addr)
#     valid = False
#     for ip in ALLOWED_IPS:
#         if client_ip.startswith(ip) or client_ip == ip:
#             valid = True
#             break
#     if not valid:
#         abort(403)

@app.route('/', methods=['POST', 'GET'])
def index():
    # Handle buttons
    if request.method == 'POST':
        action = request.form['action']
        
        print(f"Action '{action}' recieved.")

        if action == 'fireplace':
            main_functions.changeRGB(RGB_Strip.fireplace)
            # print("Fireplace button clicked")

        elif action == 'rainbow':
            main_functions.changeRGB(RGB_Strip.rainbow_cycle)
            # print("Rainbow button clicked")

        elif action == 'r6idle':
            main_functions.changeRGB(RGB_Strip.r6Idle)
            # print("r6idle button clicked")
            
        elif action == 'blinky':
            main_functions.changeRGB(RGB_Strip.eyes)
            # print("Blinky button clicked")
        
        elif action == 'flashlight':
            main_functions.changeRGB(RGB_Strip.flashlight)
            # print("Flashlight button clicked")


        elif action == "initESCs":
            main_functions.initESCs()
            # print("initESCs button clicked")

        elif action == "testMotors":
            main_functions.setSpeeds(10)
            # print("testMotors button clicked")

        return "Action received"  # You can return any response here

    return render_template('index.html')

@app.route('/live_feed')
def video():
    return Response(cam.generateFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@socketio.on('stick')
def handle_stick(data):
    x = int(data["x"]) # -100...100
    y = int(data["y"]) # -100...100

    y = min(max(y, 0), 100) # Cap speed value to 0...100 
    x = min(max(x, -100), 100) # Cap steering value to -100...100 (Sometimes gave values outside of -100...100 without capping)
    
    if y > 5: # Small deadzone
        # Map speed value to 5...10 range for ESC 
        dutyCycle = main_functions.mapValue(y, 0, 100, 500, 1000) / 100

        # % bias to motors for steering
        percentReduction = (100 - abs(x)) / 100
        
        reducedDutyCycle = 5 + (dutyCycle - 5) * percentReduction
        reducedDutyCycle = round(reducedDutyCycle, 2)

        # print(x, reducedDutyCycle - 5, dutyCycle, reducedDutyCycle)
        
        # Forward
        if x == 0:
            main_functions.setSpeedLeft(dutyCycle)
            main_functions.setSpeedRight(dutyCycle)

        # Turn Left
        elif x < 0:
            main_functions.setSpeedRight(dutyCycle)
            main_functions.setSpeedLeft(reducedDutyCycle)

        # Turn Right
        else:
            main_functions.setSpeedRight(reducedDutyCycle)
            main_functions.setSpeedLeft(dutyCycle)
    
    else: # Motors off
        main_functions.setSpeedLeft(5)
        main_functions.setSpeedRight(5)



if __name__=="__main__":
    socketio.run(app, debug=False, host = '0.0.0.0')