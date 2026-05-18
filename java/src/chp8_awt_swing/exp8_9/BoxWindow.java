package chp8_awt_swing.exp8_9;

import java.awt.Component;
import java.awt.Container;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;

public class BoxWindow extends JFrame {
     
    public BoxWindow() {
        Container contentPane = getContentPane();
        contentPane.setLayout(new BoxLayout(contentPane,
                                            BoxLayout.Y_AXIS));
   
        addAButton("Button 1", contentPane);
        addAButton("2", contentPane);
        addAButton("Button 3", contentPane);
        addAButton("Long-Named Button 4", contentPane);
        addAButton("Button 5", contentPane);

        addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) {
                System.exit(0);
               
            }
        });
    }

    private void addAButton(String text, Container container) {
        JButton button = new JButton(text);
        button.setAlignmentX(Component.CENTER_ALIGNMENT);
        container.add(button);
    }

    public static void main(String args[]) {
        BoxWindow window = new BoxWindow();

        window.setTitle("BoxLayout");
        window.pack();
        window.setVisible(true);
    }
}
