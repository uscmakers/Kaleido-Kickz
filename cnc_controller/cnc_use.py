import subprocess
import threading
import time
import os
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
SWITCH_PIN = 16
DEBOUNCE_TIME_MS = 200

GPIO.setup(SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# create a G-code file for calibration
def generate_gcode(filename="generated.gcode"):
    gcode_commands = [
        "G21", 
        "G90",  
        "G0 X10 Y10", 
        "G1 X50 Y50 F100",  
        "G1 X0 Y0 F100",  
        "M30"  
    ]

    with open(filename, "w") as f:
        for command in gcode_commands:
            f.write(command + "\n")

    print(f"G-code file '{filename}' created.")

# check if the limit switch is triggered
def check_limit_switch():
    return GPIO.input(SWITCH_PIN) == GPIO.LOW  # LOW means the switch is pressed

# monitor the limit switch
def monitor_limit_switches():
    while process.poll() is None:  
        if check_limit_switch():
            print(" Limit switch triggered! Stopping CNC operation.")
            process.terminate() 
            break
        time.sleep(0.1)


def main():
    generate_gcode("generated.gcode") 
    global process  
    process = subprocess.Popen(
        ["pycnc", "generated.gcode"],  
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    # start limit switch monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_limit_switches, daemon=True)
    monitor_thread.start()

    # read CNC process output
    for line in process.stdout:
        print(line.strip())

    process.wait()
    monitor_thread.join()
    print("CNC Operation Completed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted. Cleaning up GPIO...")
        GPIO.cleanup()