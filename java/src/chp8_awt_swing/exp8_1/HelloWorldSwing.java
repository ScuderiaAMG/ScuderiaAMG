package chp8_awt_swing.exp8_1;
import javax.swing.JFrame;
import javax.swing.JLabel;  
//import java.awt.event.*;  
public class HelloWorldSwing {
    public static void main(String[] args) {
        JFrame frame = new JFrame("HelloWorldSwing");
        final JLabel label = new JLabel("Hello World!");
        frame.getContentPane().add(label);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(2000,700);
        frame.setVisible(true);
    }
}