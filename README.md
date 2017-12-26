# Python_Arduino_plotter

Program Arduino Uno with the provided example code. It sends analog values from pin A0.

Run "experiment_new.py" to open GUI. 
Select a port where you connected Arduino and press "Connect" button to start serial communication with the board.
Baudrate is hardcoded at 115200 baud. In GUI one can also change scale of y-axis (Y min & Y max) and rate frequency of incoming data (refresh rate).
Also, beside plotting the data one can also record data in .csv file.

Note:
GUI stops working when refresh rate is set below 5 ms. 