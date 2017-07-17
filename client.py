import socket
import sys
import os
import time

def howToUse():
    print("Please inform this way the file and arguments you will send to the server:")
    print("python " + __file__ + " <host> <port> <file path>")
    sys.exit()

def sendFile(host, port, coordinatesFileName):
    message = actualSocket.recv(1024)
    if (message == "READY"):
	print("Sending file to " + host + ":" + str(port))

	try:
            coordinatesFile = open(coordinatesFileName, 'rb')
            reading = coordinatesFile.read(4096)
            actualSocket.send(reading)
            while reading != "":
		reading = coordinatesFile.read(4096)
		actualSocket.send(reading)

	    # waiting for finishing the file send
	    time.sleep(0.1)
	    actualSocket.send("-END-")
	    coordinatesFile.close()
	    response = actualSocket.recv(1024)

	    # If the file has been uploaded successfully receives a file with the coordinates
            if (response == "FINISHED"):
                print("Succesfully uploaded file.")

                coordinatesFileNameResponse = coordinatesFileName + 'Response'
                finalFile = open(coordinatesFileNameResponse, 'wb')
                actualSocket.send("READY")
                print("Receiving file...")

                while True:
                    response = actualSocket.recv(4096)
                    if (response == "-END-"):
                        finalFile.close()
                        break
                    finalFile.write(response)

                actualSocket.send("FINISHED")
                print("File succesfully received as " + coordinatesFileNameResponse)
		
		sys.exit()
	    else:
		print("Failed to upload file.")
                actualSocket.close()
	except Exception as msg:
	    print("Error message: " + str(msg))
	    return False

	return True

    elif (message == "ERROR"):
	print("Error: An unexpected error has occoured at the server side. Try again?")
	return False
    else:
	print("Error: Didn't expect the message: " + message)
	return False

######################################
########### Main Function ############
######################################

# First, try to catch the system arguments to use
try:
    host = sys.argv[1]
    port = int(sys.argv[2])
    filePath = sys.argv[3]

except:
    howToUse()

# Create a socket that use IPV4 and TCP protocol
actualSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if (os.path.exists(filePath)):
    try:
	actualSocket.connect((host, int(port)))
	print("Connected!")
    except socket.error as sem:
	print("ERROR: Couldn't connect.")
	print(sem)
	sys.exit()

    actualSocket.send("GETFILE")
    sendFile(host, port, filePath)

else:
    print("File does not exists.")
    sys.exit()
