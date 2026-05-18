package chp7_io.exp7_12;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
public class CopyBytesWithChannel {
	private static final int BSIZE = 1024;  //定义缓冲区大小
    public static void main(String[] args) throws IOException {   	
        FileInputStream inStream = new FileInputStream("src\\chp7_io\\exp7_12\\farrago.txt");
        FileOutputStream outStream = new FileOutputStream("src\\chp7_io\\exp7_12\\outagain.txt");
        FileChannel inChannel = inStream.getChannel(); //获取该文件输入流的通道
        FileChannel outChannel = outStream.getChannel(); //获取该文件输出流的通道
        ByteBuffer buffer = ByteBuffer.allocate(BSIZE);  //创建缓冲区   
        while ((inChannel.read(buffer))!= -1){
           buffer.flip();               // 使缓冲区准备好写操作         
           outChannel.write(buffer);
           buffer.clear();  // 使缓冲区准备好读操作
        }
        inStream.close();
        outStream.close();
    }
}
