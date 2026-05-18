package chp8_awt_swing.exp8_2;

import java.awt.BorderLayout;
import java.awt.Dimension;

//import java.awt.event.*;
import javax.swing.JFrame;
import javax.swing.JLabel;

public class JFrameDemo {
    public static void main(String s[]) throws Exception{
        
        //指定使用当前的Look&Feel装饰窗口。必须在创建窗口前设定。
		//System.out.println(UIManager.getCrossPlatformLookAndFeelClassName());
		//UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
		//UIManager.setLookAndFeel("javax.swing.plaf.metal.MetalLookAndFeel");
		//UIManager.setLookAndFeel("com.sun.java.swing.plaf.windows.WindowsLookAndFeel");
		//UIManager.setLookAndFeel("com.sun.java.swing.plaf.mac.MacLookAndFeel");

        JFrame.setDefaultLookAndFeelDecorated(true);

        //创建并设定关闭窗口操作。
        JFrame frame = new JFrame("JFrameDemo");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        //创建一个JLable并加到窗口中。
        JLabel emptyLabel = new JLabel("");
        emptyLabel.setPreferredSize(new Dimension(1750, 1000));
        frame.getContentPane().add(emptyLabel, BorderLayout.CENTER);

        //显示窗口。
        frame.pack();
        frame.setVisible(true);
    }
}
