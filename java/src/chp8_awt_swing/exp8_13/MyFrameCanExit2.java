package chp8_awt_swing.exp8_13;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.JFrame;
public class MyFrameCanExit2 extends JFrame {
	public static void main(String args[ ]){
		MyFrameCanExit2 fr = new MyFrameCanExit2("Hello !");
		fr.addWindowListener( fr.new WindowHandler());   //×¢²á´°¿ÚÊÂ¼þ¼àÌýÆ÷¡£
		fr.setSize(200,200);				  
		fr.setVisible(true);				
	}
		  
	public MyFrameCanExit2(String str){
		super(str);
	}
	class WindowHandler extends WindowAdapter{
		public void windowClosing(WindowEvent e) { 
    		System.exit(0);
    	}
    }
}