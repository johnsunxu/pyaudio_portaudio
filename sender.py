import sys
import socket
import sounddevice as sd
import soundfile as sf
import pyaudio

p = pyaudio.PyAudio()

#Get list of WASAPI devices
devices = []

for i in range(0, p.get_device_count()):
    device = p.get_device_info_by_index(i)
    if (p.get_host_api_info_by_index(device["hostApi"])["name"]).find("WASAPI") != -1:
        if not device["maxInputChannels"] > 0:
            devices.append(device)

for device in devices: 
    print(f"{devices.index(device)}", device["name"])

#Get device info
defaultframes = 1136
device_info = p.get_device_info_by_index(devices[(int(input("Enter index of an audio device above: ").strip()))]["index"])
rate = int(device_info["defaultSampleRate"])

#create connection
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

clientSocket.connect(("192.168.2.53", 9090))

#Send device parameters to receiver
data = str(rate).encode()
clientSocket.send(data)

#Open stream
channelcount = device_info["maxInputChannels"] if (
    device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]
inputStream = p.open(format=pyaudio.paFloat32,
                channels=channelcount,
                rate = rate,
                input=True,
                frames_per_buffer=defaultframes,
                input_device_index=device_info["index"],
                as_loopback=True)

while True:
    temp = inputStream.read(9088)
    clientSocket.send(temp)
