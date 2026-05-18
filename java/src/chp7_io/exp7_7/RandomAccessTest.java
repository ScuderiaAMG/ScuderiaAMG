package chp7_io.exp7_7;
import java.io.RandomAccessFile;
public class RandomAccessTest{
    public static void main(String args[]) throws Exception{
	    long filePoint = 0 ;
	    String s;
        RandomAccessFile file = new RandomAccessFile("src\\chp7_io\\exp7_7\\RandomAccessTest.java","r");
        long fileLength = file.length();
	    while (filePoint<fileLength){
		    s = file.readLine();
		    System.out.println(s);
		    filePoint = file.getFilePointer();
	    }
	    file.close();
    }
}