import serial
import sys
import time

# get the port anf filename from the command line arguments
saved_file = sys.argv[1]
port = sys.argv[2]
label = sys.argv[3]
ser = serial.Serial(port,9600) #ポートの情報を記入
i = 0
# wait 2 second for the serial connection to establish
time.sleep(2)
for i in range(10):
    ser.readline()
while(i < 100):
    value = ser.readline().decode('utf-8').rstrip().rstrip(',')
    print(i,value)
    with open(saved_file, 'a') as f:
        print('{},{},{}'.format(i,label,value),file=f)
    i += 1
