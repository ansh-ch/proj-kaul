import java.io.*;
import java.net.*;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.UnknownHostException;
import java.io.File;
import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.OutputStream;


import java.io.BufferedOutputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.InetAddress;


public class Udp_Comm {

	public void udpServer(String fileName, int portNo, long fileSize) throws UnknownHostException, IOException 
	{
		try
		(
			DatagramSocket socket = 
					new DatagramSocket(portNo);
		)
		{
			
			byte[] contents = new byte[256];
			DatagramPacket packet = new DatagramPacket(contents, contents.length);
			
	        FileOutputStream fos = new FileOutputStream(fileName);
			BufferedOutputStream out_file = new BufferedOutputStream(fos);
			
			int bytesRecv = 0;
			
			while(fileSize > bytesRecv )
			{
				packet = new DatagramPacket(contents, contents.length);
	            socket.receive(packet);
	            if (contents.length > 0)
	            {
	            	bytesRecv += contents.length;
	            	out_file.write(contents, 0, contents.length);
	                System.out.print("\rRecv file ... "+(bytesRecv*100)/fileSize+"%!");

	            }	            				
			}

			
	        out_file.flush(); 
	        out_file.close();
	        socket.close();
			            
	        System.out.println("File saved ! "+(bytesRecv*100)/fileSize+"%");

		} 
		catch (IOException e) {
			System.out.println("Exception caught when trying to listen on port "
				+ portNo + " or listening for a connection");
			System.out.println(e.getMessage());
        }
		
	}



	public void udpClient(String fileName, int portNo, long fileSize) throws UnknownHostException, IOException 
	{
		try
		(
			DatagramSocket socket = 
					new DatagramSocket();
		)
		{
			
    		File file = new File(fileName);
            FileInputStream fis = new FileInputStream(file);
            BufferedInputStream bis = new BufferedInputStream(fis); 

            long fileLength = file.length(); 
			byte[] contents = new byte[256];
            long current = 0;
            
			DatagramPacket packet = new DatagramPacket(contents, contents.length, InetAddress.getByName("localhost"), portNo);
						
            while(current!=fileLength){ 
                int size = 256;
                if(fileLength - current >= size)
                    current += size;    
                else{ 
                    size = (int)(fileLength - current); 
                    current = fileLength;
                } 
                contents = new byte[size]; 
                bis.read(contents, 0, size);
                packet = new DatagramPacket(contents, contents.length, InetAddress.getByName("localhost"), portNo);
                
                Thread.sleep(4);
                socket.send(packet);
                System.out.print("\rSending file ... "+(current*100)/fileLength+"% complete!");
            }

			socket.close();
			bis.close();
			fis.close();
			            
	        
		} 
		catch (IOException e) {
			System.out.println("Exception caught when trying to listen on port "
				+ portNo + " or listening for a connection");
			System.out.println(e.getMessage());
	    } catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
}
