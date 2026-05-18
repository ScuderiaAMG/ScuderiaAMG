package chp7_io.exp7_8;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.util.Date;
public class SerializeDate {
    Date d ;
    SerializeDate( ){
		d= new Date( );
		try {
	  	 	FileOutputStream f = new FileOutputStream("date.ser");
	   	 	ObjectOutputStream s= new ObjectOutputStream(f);
	    	s.writeObject(d);
	    	f.close( );
	    	}catch( IOException e){
				e.printStackTrace( );
				}
		}
public static void main(String args[]){
	 SerializeDate b =new SerializeDate();
	 System.out.println("The saved date is :"+b.d.toString());
	 }
}
