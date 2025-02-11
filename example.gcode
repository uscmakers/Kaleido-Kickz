G21        ; Set units to millimeters
G90        ; Absolute positioning
G0 X10 Y10 ; Move to X=10mm, Y=10mm rapidly
G1 X50 Y50 F100 ; Move to X=50mm, Y=50mm at feed rate of 100
G1 X0 Y0 F100   ; Move back to origin
M30        ; End of program