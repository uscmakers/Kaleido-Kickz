# gcode_parser.py

import re
from motor_control import set_direction, step_motor

def parse_gcode(file_path):
    """
    Parse a G-code file and execute motor commands.
    :param file_path: Path to the G-code file
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith(';'):  # Skip empty lines and comments
            continue

        command = line.split()[0]

        if command in ['G0', 'G1']:
            # Extract X and Y coordinates if present
            x_match = re.search(r'X([-+]?\d*\.?\d+)', line)
            y_match = re.search(r'Y([-+]?\d*\.?\d+)', line)

            x = float(x_match.group(1)) if x_match else 0.0
            y = float(y_match.group(1)) if y_match else 0.0

            # Determine direction based on X and Y
            if x > 0:
                set_direction('CW')
            elif x < 0:
                set_direction('CCW')

            # Calculate steps (this is a simplistic approach)
            steps = int(abs(x) * 100)  # Adjust the multiplier based on your setup
            step_motor(steps)

            # Similarly handle Y if applicable
            if y != 0:
                if y > 0:
                    set_direction('CW')
                else:
                    set_direction('CCW')
                steps = int(abs(y) * 100)  # Adjust as needed
                step_motor(steps)

        # Handle other G-code commands as needed

    # After execution, cleanup GPIO
    from motor_control import cleanup
    cleanup()
