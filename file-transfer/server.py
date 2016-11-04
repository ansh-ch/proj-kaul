import socket,os,hashlib,signal,re,time
from datetime import datetime

def init():
	if not os.path.exists("sharing"):
		os.makedirs("sharing")
	
	host = '127.0.0.1'
	port = 12345
	sockfd = socket.socket()
	sockfd.bind((host,port))
	sockfd.listen(5)
	return sockfd

def SinceEpoch(dt):
	epoch = datetime(1970,1,1)
	dt = datetime.strptime(dt, "%d-%m-%Y %H:%M:%S")
	return (dt-epoch).total_seconds()

def ConvertToDatetime(time):
	return datetime.fromtimestamp(time).strftime("%d-%m-%Y %H:%M:%S")

def SendFilelist(sockfd,args) :
	shared = "sharing"
	print len(args)
	if(len(args) == 6) :
		sts = SinceEpoch(args[2]+ " " + args[3])
		ets = SinceEpoch(args[4]+ " " + args[5])
		
	for filename in os.listdir(shared) :
		filepath = shared + '/' + filename
		if(len(filename.split('.')) >= 2) :
			ext = filename.split('.')[-1]
		else :
			ext = "unknown"
			
		if args[1] == "shortlist" :
			modtime = os.path.getmtime(filepath)
			if sts<modtime and modtime<ets  :
				data = sockfd.send(filename + " " + str(os.path.getsize(filepath)) + "  " + str(ConvertToDatetime(os.path.getmtime(filepath))) + "  " + ext + '\n')
		elif args[1] == "longlist" :
			data = sockfd.send(filename + " " + str(os.path.getsize(filepath)) + "  " + str(ConvertToDatetime(os.path.getmtime(filepath))) + "  " + ext + '\n')
		elif args[1] == "regex" :
			if re.search(args[2],filename) :
				data = sockfd.send(filename + " " + str(os.path.getsize(filepath)) + "  " + str(ConvertToDatetime(os.path.getmtime(filepath))) + "  " + ext + '\n')
	data = sockfd.send("NULL")
	print "Exiting File list sending"
	
def CheckFile(sockfd,checkname):
	shared = "sharing"
	#checkname = sockfd.recv(1024)
	print "Received filename to check for" + checkname
	for filename in os.listdir(shared) :
		print filename
		filepath = shared + '/' + filename
		if filename == checkname :
			with open(filepath) as ftemp :
				content = ftemp.read()
				message = hashlib.md5(content).hexdigest()+ "  " + str(ConvertToDatetime(os.path.getmtime(filepath)))
				#print message
				data = sockfd.send(message)
				return

	data = c.send("File " + checkname + " not found\n")
	
def CheckAllFiles(sockfd):
	shared = "sharing"
	print "Received filename to check for"
	for filename in os.listdir(shared) :
		print filename
		filepath = shared + '/' + filename
		with open(filepath) as ftemp :
			content = ftemp.read()
			data = sockfd.send(filename + "  " + hashlib.md5(content).hexdigest()+ "  " + str(ConvertToDatetime(os.path.getmtime(filepath))) + "\n")
	sockfd.send("NULL");
	
def SendFile(sockfd,filename) :
	filepath = "sharing/" + filename

	try :
		fread = open(filepath,'rb')
	except :
		print "File Doesnt exist"
		sockfd.send("-1")
	else:
		line = fread.read(1024)

		print "getting content"
		with open(filepath) as ftemp:
			content = ftemp.read()

		print "Sending receipt"
		data = sockfd.send(filename + "  " + str(os.path.getsize(filepath)) + "  " + str(ConvertToDatetime(os.path.getmtime(filepath))) +  "  " +  hashlib.md5(content).hexdigest() + "  \n")

		while line:
			data = sockfd.send(line)
			line = fread.read(1024)

		data = sockfd.send("NULL")
		fread.close()
	
def close(sockfd):
	sockfd.close()

def UDPSend(filename):
	host = "127.0.0.1"
	port = 8000

	sockudp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sockudp.bind((host, port))

	try :
		print "HELLO FROM SERVER"
		data,addr = sockudp.recvfrom(1024)
		filepath = "sharing/" + filename
		fread = open(filepath,'rb')
	except :
		print "File Doesnt exist"
		sockudp.sendto("NULL",addr)
	else:
		print "Client says" + data
		line = "abc"
		while line:
			line = fread.read(1024)
			sockudp.sendto(line,addr)

		
		filepath = "sharing/" + filename
		with open(filepath) as ftemp:
			content = ftemp.read()
			
		line = filename + "  " + str(os.path.getsize(filepath)) + "  " + str(ConvertToDatetime(os.path.getmtime(filepath))) +  "  " +  hashlib.md5(content).hexdigest() + "  \n"
		
		sockudp.sendto(line,addr)
		fread.close()
		
	finally:
		sockudp.close()

	
if __name__ == "__main__" :

	while 1:
		tsock = init()
		c,addr = tsock.accept()
		print "Connected to " + str(addr)
		history = []
		while True:
			command = c.recv(1024)
			if not command:
				break;

			print command

			history.append(command)
			args = command.split(" ")
			command = args[0]

			if command == "indexget" :
				SendFilelist(c,args)
			elif command == "filehash" :
				if args[1] == "verify" :
					CheckFile(c,args[2])
				elif args[1] == "checkall" :
					CheckAllFiles(c)
			elif command == "filedownload" :
				if args[1].lower() == "tcp" :
					SendFile(c,args[2])
				elif args[1].lower() == "udp" :
					UDPSend(args[2])
			else :
				print "Invalid command"

		close(c)		
		close(tsock)
