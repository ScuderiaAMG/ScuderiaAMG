package chp8_awt_swing.exp8_14;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.JFrame;
public class MyFrameCanExit3 extends JFrame {
	public static void main(String args[ ]){
		MyFrameCanExit3 fr = new MyFrameCanExit3("Hello !");
		fr.addWindowListener( new WindowAdapter(){
				public void windowClosing(WindowEvent e) { 
    				System.exit(0);
    			}
    	});   //×¢²á´°¿ÚÊÂ¼þ¼àÌýÆ÷¡£
		fr.setSize(200,200);				   
		fr.setVisible(true);				
	}
		  
	public MyFrameCanExit3(String str){
		super(str);
	}	
}