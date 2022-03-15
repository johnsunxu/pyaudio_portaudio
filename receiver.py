import sys
import os
import socket
import sounddevice as sd
import threading
import pyaudio

p = pyaudio.PyAudio()

#Get list of devices
# inputDevices = []
outputDevices = []
for i in range(0, p.get_device_count()):
    device = p.get_device_info_by_index(i)
    # print(device)
    if device["maxInputChannels"] > 0 and device["maxOutputChannels"] > 0:
        outputDevices.append(device)
    # elif device["maxInputChannels"] > 0:
    #     inputDevices.append(device)
    else:
        outputDevices.append(device)

if len(outputDevices) == 0:
    print("No compatible devices found.")
    sys.exit(0)

for device in outputDevices:
    print(f"{outputDevices.index(device)}",
          device["name"], "Sample rate:", device["defaultSampleRate"])

#Get device info
device_info = p.get_device_info_by_index(outputDevices[(
    int(input("Enter index of an output audio device above: ").strip()))]["index"])

#Create server
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverSocket.bind(("192.168.2.53", 9090))

serverSocket.listen()

(clientConnected, clientAddress) = serverSocket.accept()

print("Accepted a connection request from %s:%s" %
      (clientAddress[0], clientAddress[1]))

#Establish connection
inputRate = int(str(clientConnected.recv(128).decode()))
outputRate = device_info["defaultSampleRate"]

if outputRate != inputRate:
    print(outputRate, inputRate)
    print("""WARNING: Input device has a different sample rate than the output device. 
    This is highly discouraged. 
    Please change your input or output device settings for best performance.""")

sd.default.blocksize = 0

event = threading.Event()
while True:
    try:
        current_frame = 0

        def callback(outdata, frames, time, status):
            global current_frame
            if status:
                print(status)

            #Number of bytes that should be received for each format
            #6816 int24 41 400
            #9088 float32 41 400
            #9984 float32 48 000

            dataFromClient = clientConnected.recv(
                len(outdata[:]), socket.MSG_WAITALL)

            outdata[:] = dataFromClient
            #Error opening RawOutputStream: Invalid number of channels [PaErrorCode -9998] solve later, maybe something to do with hostapi
        stream = sd.RawOutputStream(samplerate=outputRate, device=(
            device_info["index"]), callback=callback, finished_callback=event.set)
        with stream:
            event.wait()
    except Exception as e:
        print(e)
        serverSocket.close()
