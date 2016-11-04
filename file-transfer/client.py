import socket,re,time
import os,hashlib,signal
from datetime import datetime

def init() :
	if not os.path.exists("sharing"):
		os.makedirs("sharing")

		
	host = '127.0.0.1'
	port = 12345
	sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockfd.settimeout(4)
	return sockfd,host,port

def ReceiveFilelist(sockfd,flag):
	output = ""
	try :
		line = "abc"
		while 1:
			line = sockfd.recv(1024)
			if line[-4:] == "NULL" :
				output += line[:-4]
				break
			output += line
							
	except socket.error :
		print "File recv timed out"

	else :
		print "File list received"
	finally :
		print '\n\n'
		print output
		print '\n\n'
		print "Exit Receive function"
	
def ReceiveFile(sockfd,filename):
	try :
		content = ""
		while 1:
			line = sockfd.recv(1024)
			if line[-4:] == "NULL" :
				content += line[:-4]
				break
			content += line
			
		linelist = content.split("\n",1)
		print linelist[0]
		content = linelist[1]
		line = linelist[0]
		
	except socket.error :
		print "File recv timed out"
		if(line == "-1"):
			print "File Doesnt exist"
	else :
		fwrite = open(filename,"wb")
		fwrite.write(content)
		fwrite.close()
		
		args = line.split("  ")
		print '\n\n'
		print args
		with(open(filename,"rb")) as ftemp:
			content = ftemp.read()

		print hashlib.md5(content).hexdigest()
		print '\n\n'
		
		if(hashlib.md5(content).hexdigest() == args[len(args)-2]) :
			print "File Hash Checked. Receive succesful"
		else :
			print "File is damaged. Request for File again"
	
def RequestFileCheck(sockfd,filename):
	line = sockfd.recv(1024)
	print line

def RequestFolderCheck(sockfd):
	line = 'abc'
	output = ""
	try :
		while line:
			line = sockfd.recv(1024)
			if line[-4:] == "NULL" :
				output += line[:-4]
				break			
			output += line
		print output
		
	except socket.error :
		print "File recv timed out"

def TestCommand(arr):
	if len(arr) < 2:
		print "Invalid Command"
		return False
	
	if arr[0].lower() == "indexget" :
		if arr[1].lower() == "shortlist" :
			if len(arr) == 6:
				try :
					datetime.strptime(arr[2] + " " + arr[3], "%d-%m-%Y %H:%M:%S")
					datetime.strptime(arr[2] + " " + arr[3], "%d-%m-%Y %H:%M:%S")
				except ValueError:
					print "Invalid Date input"
					return False
				else :
					return True
			else :
				print "Invalid number of parameters"
				return False
		elif arr[1].lower() == "longlist" :
			return True
		elif arr[1].lower() == "regex" :
			if len(arr) >= 3 :
				return True
		else :
			print "Incorrect Flag"
			
	elif args[0].lower() == "filehash" :
		if arr[1].lower() == "verify" :
			if len(arr) >= 3 :
				return True
			else :
				print "Incorrect number of arguments"
				return False
		elif arr[1].lower() == "checkall" :
			if len(arr) >= 2:
				return True
			else :
				return False
		else :
			print "Incorrect Flag"
			return False
	elif args[0].lower() == "filedownload" :
		if arr[1].lower() == "tcp" or arr[1].lower() == "udp" :
			if len(arr) >= 3:
				return True
			else :
				print "Incorrect Number of arguments"
				return False
		else :
			print "Invalid Flag"
			return False
	else :
		print "Invalid Command"
		return False
		
def close(sockfd):
	sockfd.close()

def UDPReceive(filename):
	sockudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	host = '127.0.0.1'
	port = 8000
	message = "Hello From Client Side"
	time.sleep(4)
	content = ""
	print "HELLO THERE"
	sockudp.sendto(message, (host, port))
	while 1:
		data, addr = sockudp.recvfrom(1024)
		if not data:
			break
		if data == "NULL" :
			content = "NULL"
			break
		content += data

	if(content != "NULL"):
		fwrite = open(filename,"wb")
		fwrite.write(content)
		fwrite.close()
		data, addr = sockudp.recvfrom(1024)
		print data
		print "File Downloaded"
	else :
		print "File not found"
		
	sockudp.close()
	
if __name__ == "__main__" :
	tsock,host,port = init()
	tsock.connect((host, port))
	command = ""
	while True:
		while not command :
			command = raw_input("$> ")
			
		if command == "exit" :
			break;

		args = command.split(" ")
		if(TestCommand(args)):
			tsock.send(command)
			command = args[0].lower()

			if command == "indexget" :
				ReceiveFilelist(tsock,args[1])
			elif command == "filehash" and args[1] == "verify" :
				RequestFileCheck(tsock,args[2])
			elif command == "filehash" and args[1] == "checkall" :
				RequestFolderCheck(tsock)
			elif command == "filedownload":
				if args[1].lower() == "tcp" :
					ReceiveFile(tsock,args[2])
				elif args[1].lower() == "udp" :
					UDPReceive(args[2])
			else :
				print "Invalid command"

		command = ""
	close(tsock)


