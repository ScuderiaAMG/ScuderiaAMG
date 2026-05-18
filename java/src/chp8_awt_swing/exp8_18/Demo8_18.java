package chp8_awt_swing.exp8_18;

import java.awt.Color;
import java.awt.Graphics;

import javax.swing.JFrame;
import javax.swing.JPanel;

class MyPanel extends JPanel{
	public void paint(Graphics g){
		setBackground(Color.ORANGE);
		super.paint(g);
		g.setColor(Color.cyan);
		g.fill3DRect(50, 50, 200, 90, false);
		g.setColor(Color.red);
		g.drawOval(300, 300, 100, 50);
	}
}
public class Demo8_18 {
	public static void main(String[] args) {
		JFrame jf=new JFrame("Œ“ «ª≠± ");
		jf.add(new MyPanel());
		jf.setSize(500, 500);
		jf.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		jf.setVisible(true);
	}

}
