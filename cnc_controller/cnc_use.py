import subprocess
import threading
import time
import os

# function to create a G-code file for calibraiton 
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


def monitor_limit_switches():
    while process.poll() is None:  # runs while pycnc is active
       
        limit_triggered = check_limit_switch()
        if limit_triggered:
            print("⚠️ Limit switch triggered! Stopping CNC operation.")
            process.terminate()  # terminate pycnc subprocess
            break
        time.sleep(0.1)  


def check_limit_switch():
  
    return False 

def main():
    generate_gcode("generated.gcode")  

    global process  
    process = subprocess.Popen(
        ["pycnc", "generated.gcode"],  
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

   
    monitor_thread = threading.Thread(target=monitor_limit_switches, daemon=True)
    monitor_thread.start()

    for line in process.stdout:
        print(line.strip()) 


    process.wait()
    monitor_thread.join()
    print("✅ CNC Operation Completed.")

if __name__ == "__main__":
    main()