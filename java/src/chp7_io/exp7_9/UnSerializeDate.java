package chp7_io.exp7_9;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.util.Date;
public class UnSerializeDate{
	Date d = null ;
    UnSerializeDate(){
		try {
	  		FileInputStream f = new FileInputStream("src\\chp7_io\\exp7_9\\date.ser");
	  		ObjectInputStream s = new ObjectInputStream(f);
	  		d = (Date) s.readObject();
	  		f.close();
			}catch(Exception e){
				e.printStackTrace() ;
			}
	}
public  static void main(String args[]){
	UnSerializeDate a =new UnSerializeDate();
	System.out.println("The date read is :"+a.d.toString());
	}
}
