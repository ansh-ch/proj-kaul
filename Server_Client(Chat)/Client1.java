import java.io.*;
import java.net.*;

class Global{
	public static String hostName;
	public static int portNo;
	public static int lportNo;
	
}

class Risv implements Runnable{
	private Thread t;
	private String threadName;
	private String threadProt;
	
	Risv (String t_name, String t_prot)
	{
		threadName = t_name;
		threadProt = t_prot;
		System.out.println("Creating " + threadName);
	}
	
	
	
	public int listener(String hostName, int portNo)
	{

        try (
                Socket recvSocket = new Socket(hostName, portNo);
                PrintWriter out =
                    new PrintWriter(recvSocket.getOutputStream(), true);
                BufferedReader in =
                    new BufferedReader(
                        new InputStreamReader(recvSocket.getInputStream()));
            ) {
        		System.out.print(recvSocket);
                String inNow;
                while ((inNow = in.readLine()) != null) {
                	
                    System.out.println("recv: "+ inNow);

                    String[] tokens = inNow.split(" ");
                	String trim = inNow.trim();
                	String fileName = "";
                	String protocol = "";
                	long fileSize = -1;
                	int port = -1;
                	int len = 0;
                	
                	if (!trim.isEmpty())
                	    len = trim.split("\\s+").length;
                	
                	int fileTransferFlag = 0;
                	if (len == 5)
                	{
                		len = 0;
                		for (String token : tokens) {
                			if(len == 0  && token.equals("Sending"))
                				fileTransferFlag = 1;
                			if(fileTransferFlag == 1 && len == 1)
                				fileName = token;
                			if(fileTransferFlag == 1 && len == 2)
					    port = Integer.parseInt(token);
                			if(fileTransferFlag == 1 && len == 3)
					    protocol = token;
					if(fileTransferFlag == 1 && len == 4)
					    fileSize = Long.parseLong(token);
                			len = len + 1;
                		}
                		if (fileTransferFlag == 1)
                		{
                			
                			protocol = protocol.toLowerCase();
            				//File file = new File(fileName);
            				//fileSize = file.length();

            				if(protocol.equals("tcp"))
            				{	
        						Tcp_Comm tcp1 = new Tcp_Comm();
                			
        						int dummy =0;
        						while (dummy != 1)
        							dummy = tcp1.trecv(fileName, port, fileSize);
            				}
                			else if (protocol.equals("udp"))
                			{
                				System.out.println("UDP Listen");
                				Udp_Comm udp1 = new Udp_Comm();
                				
                				udp1.udpServer(fileName, port, fileSize);
                			}

                		}
                	}                    
                } 
                //in.close();
                //out.close();
                recvSocket.close();
                
            } catch (UnknownHostException e) {
                System.err.println("Don't know about host " + hostName);
                System.exit(1);
            } catch (IOException e) {
                System.err.println("Couldn't get I/O for the connection to " +
                    hostName);
                //System.exit(1);
                return 0;
            }		
		return 1;
	}
	
	public void sender(String hostName, int portNo)
	{
        try (
                ServerSocket serverSocket =
                    new ServerSocket(portNo);
                Socket clientSocket = serverSocket.accept();     
                PrintWriter out =
                    new PrintWriter(clientSocket.getOutputStream(), true);                   
                BufferedReader in = new BufferedReader(
                    new InputStreamReader(clientSocket.getInputStream()));
                BufferedReader stdIn =
                	new BufferedReader(
                		new InputStreamReader(System.in));
            ){
                String userInput;
                while ((userInput = stdIn.readLine()) != null) {
                	String[] tokens = userInput.split(" ");
                	String trim = userInput.trim();
                	String fileName = "";
                	String protocol = "";
                	long fileSize = -1;
                	int port = -1;
                	int len = 0;
			
                	
                	if (!trim.isEmpty())
                	    len = trim.split("\\s+").length;
                	
                	int fileTransferFlag = 0;
                	if (len == 4)
                	{
                		len = 0;
                		for (String token : tokens) {
                			if(len == 0  && token.equals("Sending"))
                				fileTransferFlag = 1;
                			if(fileTransferFlag == 1 && len == 1)
                				fileName = token;
                			if(fileTransferFlag == 1 && len == 2)
                    			port = Integer.parseInt(token);
                			if(fileTransferFlag == 1 && len == 3)
                    			protocol = token;
                			len = len + 1;
                		}
                		if (fileTransferFlag == 1)
                		{
                			protocol = protocol.toLowerCase();
                			System.out.println(fileName + " "+port+" "+ protocol);
            				File file = new File(fileName);
            				fileSize = file.length();
					userInput = userInput + " " + String.valueOf(fileSize);

                			
                			if(protocol.equals("tcp"))
                			{
                				Tcp_Comm tcp1 = new Tcp_Comm();
                				out.println(userInput);
                		    
                				tcp1.tsend(fileName, port);
                			}
                			else if (protocol.equals("udp"))
                			{
                				System.out.println("UDP");
                				Udp_Comm udp1 = new Udp_Comm();
                				out.println(userInput);

                				udp1.udpClient(fileName, port, fileSize);
                			}
                		}
                	}
            		if (fileTransferFlag != 1)                	
            			out.println(userInput);
                }
                clientSocket.close();
                serverSocket.close();
            } catch (IOException e) {
                System.out.println("Exception caught when trying to listen on port "
                    + portNo + " or listening for a connection");
                System.out.println(e.getMessage());
            }
		
	}
	

	@Override
	public void run() {
		Global globe1 = new Global();
		
		if (threadName == "send")
			sender(globe1.hostName, globe1.portNo);
		else
			if (threadName == "recv")
			{
				int dummy = 0;
				while(0 == dummy)
				{dummy = listener(globe1.hostName, globe1.lportNo);}
			}
	}

	public void start() {
		// TODO Auto-generated method stub
		System.out.println("leaf");
		if (t == null){
			t = new Thread(this, threadName);
			t.start();
		}
		
	}
}


public class Client1{

	public static void main(String[] args){
         
        if (args.length != 3) {
            System.err.println(
                "Usage: java EchoClient <host name> <port number> <listen port number>");
            System.exit(1);
        }
 
        Global globe = new Global();
        globe.hostName = args[0];
        globe.portNo = Integer.parseInt(args[1]);
        globe.lportNo = Integer.parseInt(args[2]);
        
 
        Risv r1 = new Risv("send", "tcp");
        r1.start();
        Risv r2 = new Risv("recv", "tcp");
        r2.start();
        
   }
}
