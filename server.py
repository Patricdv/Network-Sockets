import socket
import thread
import sys
import os
import time
import uuid
from math import radians, cos, sin, asin, sqrt

HOST = ''
PORT = 50005

def calculateHaversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r

def calculateDistance(fileName):
    # Function that reads the coordinates in file and send to haversine formula

    actualFile = open(fileName, "rb+")
    lines = actualFile.readlines()
    actualFile.seek(0)
    actualFile.truncate()
    for line in lines:
        actualFile.write('(')
	line = line.replace("(", "")
	line = line.replace(")", "")
	line = line.replace(" ", "")
	line = line.replace("\n", "")
	line = line.replace("\r", "")
	
	coordinates = line.split(",")
	for coordinate in coordinates:
            actualFile.write(str(coordinate) + ', ')
	
	distance = calculateHaversine(float(coordinates[0]), float(coordinates[1]), float(coordinates[2]), float(coordinates[3]))    
        actualFile.write(str(distance) + ')\n')
    actualFile.close()

def connect(connection):
    # Connect with the client and generate a unique filename
    fileName = "received-files/" + str(uuid.uuid4())

    try:
        # Save the coordinates file on the server directory
        file = open(fileName, 'wb')
        connection.send("READY")
        print("Downloading file...")

        while True:
            response = connection.recv(4096)
            if (response == "-END-"):
                file.close()
                break
            file.write(response)

        connection.send("FINISHED")
        print("Succesfully downloaded file as " + fileName)

        #########################################################
	# Calculate the distance between the points and respond #
        #########################################################

        calculateDistance(fileName)

        message = connection.recv(1024)
        if (message == "READY"):
            try:
                finalFile = open(fileName, 'rb')
                reading = finalFile.read(4096)
                connection.send(reading)
                while reading != "":
                    reading = finalFile.read(4096)
                    connection.send(reading)
                
                # waiting for finishing the file send
                time.sleep(1)
                connection.send("-END-")
                
                print("finished sending")
                finalFile.close()

                response = connection.recv(1024)

                # If the file has been sended successfully
                if (response == "FINISHED"):
                    print("File succesfully sended.")
                else:
                    print("Failed to send file.")

                connection.close()
            except Exception as msg:
                print("Error on send file:" + msg)
                connection.close()
        else:
            print("Error: Didn't expect the message: " + message)
            connection.close()    

        #######################################################

    except Exception as msg:
        connection.send("ERROR")
        #File Error.
        print("Error message: " + str(msg))
        return

def conectado(connection, client):
    ###Function that starts a new thread for the connection
    msg = connection.recv(1024)
    if (msg == "GETFILE"):
        print("Connection started with " + str(client))
        connect(connection)
    else:
        connection.close()
    thread.exit()

# Create a socket that use IPV4 and TCP protocol
# Bind the port for this process conections
# Set the maximun number of queued connections
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
origin = (HOST, PORT)

try:
    tcp.bind(origin)
    print("Binded")
except socket.error as SBE:
    print("Bind failed!")
    print(SBE)
    sys.exit()

tcp.listen(5)

print("TCP started and already listening...")

# Server accept connections until a keyboard interrupt
# If there is a keyboard interrupt, release the port

try:
    while True:
        connection, client = tcp.accept()

        # For every connect a new thread will be created
        thread.start_new_thread(conectado, tuple([connection, client]))

except KeyboardInterrupt:
    print("\n\n--- TCP connection ended ---")
    tcp.close()
    sys.exit()
