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

class Tcp_Comm {
	
	public int trecv(String fileName, int portNo, long fileSize) throws UnknownHostException, IOException 
	{
		try
		(
			Socket recvSocket = new Socket(InetAddress.getByName("localhost"), portNo);
		)
		{
	        byte[] contents = new byte[1024];
	        // since both in same folder, had to brute force a name
	        
	        //Initialize the FileOutputStream to the output file's full path.
	        FileOutputStream fos = new FileOutputStream(fileName);
			BufferedOutputStream out_file = new BufferedOutputStream(fos);
	        InputStream in = recvSocket.getInputStream();
	        
	        //No of bytes read in one read() call
	        int bytesRead = 0; 
	        long bytesRecv = 0;
	        
	        while((bytesRead=in.read(contents))!=-1)
	        {
	        	bytesRecv += bytesRead;
	        	System.out.print("\rSending file ... "+(bytesRecv*100)/fileSize+"% complete!");
	            out_file.write(contents, 0, bytesRead); 
	        }
	        out_file.flush(); 
	        out_file.close();
	        recvSocket.close(); 
	        
	        System.out.println("File saved successfully!");
	        return 1;

		}
		catch (IOException e) {
            System.out.println("Exception caught when trying to listen on port "
                + portNo + " or listening for a connection teeeheeeeeeee XD");
            //System.out.println(e.getMessage());
            return 0;
        }
		
	}

	public void tsend(String fileName, int portNo)
	{
        try (
                ServerSocket serverSocket =
                    new ServerSocket(portNo);
                Socket clientSocket = serverSocket.accept();     
        		OutputStream out = clientSocket.getOutputStream();
            ){

        		File file = new File(fileName);
                FileInputStream fis = new FileInputStream(file);
                BufferedInputStream bis = new BufferedInputStream(fis); 

                byte[] contents;
                long fileLength = file.length(); 
                long current = 0;
                

                while(current!=fileLength){ 
                    int size = 1024;
                    if(fileLength - current >= size)
                        current += size;    
                    else{ 
                        size = (int)(fileLength - current); 
                        current = fileLength;
                    } 
                    contents = new byte[size]; 
                    bis.read(contents, 0, size); 
                    out.write(contents);
                    System.out.print("\rSending file ... "+(current*100)/fileLength+"% complete!");
                }   
                
                out.flush(); 
                bis.close();
                fis.close();
                clientSocket.close();
                serverSocket.close();
                System.out.println("File sent succesfully!");
                
            } catch (IOException e) {
                System.out.println("Exception caught when trying to listen on port "
                    + portNo + " or listening for a connection");
                System.out.println(e.getMessage());
            }		
	}
	
}
