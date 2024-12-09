import RGB_Strip

from gpiozero import PWMOutputDevice
import time
import threading

PIN1 = 13
PIN2 = 19

motor1 = PWMOutputDevice(PIN1, frequency=50)
motor2 = PWMOutputDevice(PIN2, frequency=50)
motors = [motor1, motor2]


def setSpeed(motor: PWMOutputDevice, dutyCycle: int):
    motor.value = dutyCycle / 100 

def setSpeeds(dutyCycle: int, motors: list[PWMOutputDevice] = motors):
    for motor in motors:
        setSpeed(motor, dutyCycle)

def setSpeedRight(dutyCycle, motor = motor1):
    setSpeed(motor, dutyCycle)

def setSpeedLeft(dutyCycle, motor = motor2):
    setSpeed(motor, dutyCycle)

def initESC(motor: PWMOutputDevice):
    setSpeed(motor, 10)
    print("ESC Init: Speed at max")
    time.sleep(2)

    setSpeed(motor, 5)
    print("ESC Init: Speed at min")
    time.sleep(2)
    
    print("ESC Init Complete!")

def initESCs(ESCsToInit=motors):
    for esc in ESCsToInit:
        setSpeed(esc, 10)

    print("ESC Init: Speeds at max")
    time.sleep(2)

    for esc in ESCsToInit:
        setSpeed(esc, 5)

    print("ESC Init: Speeds at min")
    time.sleep(2)
    
    print("ESC Init Complete!")

# Converts value in range of in_min...in_max to out_min...out_max
def mapValue(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

activeRGBThread = None
stopEvent = None
threadLock = threading.Lock()
def changeRGB(RGBMode):
    global activeRGBThread, stopEvent, threadLock
    
    # Don't change if the same mode is requested
    if activeRGBThread is not None:
        if RGBMode.__name__ in activeRGBThread.name:
            return
    
    # Stop previous daemon thread
    with threadLock:
        if activeRGBThread is not None:
            stopEvent.set()  # Signal the thread to stop
            activeRGBThread.join()  # Wait for the thread to finish

        # Clear the stop event
        stopEvent = threading.Event()
    
        # Start a new daemon thread
        activeRGBThread = threading.Thread(target=RGBMode, args=(stopEvent,), daemon=True)
        activeRGBThread.start()


if __name__ == "__main__":
    ESCs_initialized = False
    
    stopEvent = threading.Event()
    
    activeThread = threading.Thread(target=RGB_Strip.fireplace, args=(stopEvent,), daemon=True)
    activeThread.start()

    #RGBThreads = [fireplace, rainbow_cycle, knight_rider]
    RGBModes = [RGB_Strip.fireplace, RGB_Strip.rainbow_cycle, RGB_Strip.knight_rider, RGB_Strip.eyes, RGB_Strip.cycle_colors, RGB_Strip.r6Idle]
    RGBWaitTimes = [0.01, 0.001, 0.05, 0.1, 0.001, 0.035]

    i = 0
    while input("any input: ") != "q":
        stopEvent.set()
        activeThread.join()
        
        i += 1
        if i > len(RGBModes) - 1:
            i = 0

        stopEvent.clear()
        
        activeThread = threading.Thread(target=RGBModes[i], args=(stopEvent,), daemon=True)
        activeThread.start()