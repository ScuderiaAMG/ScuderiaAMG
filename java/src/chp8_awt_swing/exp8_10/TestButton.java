/**
 * 【功能说明】
 * 本程序演示 Swing 按钮的基本使用和事件处理机制。
 * 点击窗口中的按钮时，控制台会输出按钮的动作事件信息。
 * 通过将 ActionListener 独立实现为外部类 ButtonHandler，
 * 展示了"分离事件处理逻辑"的经典设计模式。
 *
 * 【知识点】
 * 1. JButton —— Swing 按钮组件，可触发 ActionEvent 事件。
 * 2. addActionListener() —— 为按钮注册 ActionListener 监听器，
 *    当按钮被点击时，监听器的 actionPerformed 方法会被自动调用。
 * 3. ActionListener 接口 —— 只包含一个方法 actionPerformed(ActionEvent e)，
 *    是函数式接口（可用 Lambda 表达式简化）。
 * 4. ActionEvent —— 动作事件对象，封装了事件相关信息：
 *    - getActionCommand(): 返回与动作关联的命令字符串，默认为按钮文字
 *    - getSource(): 返回事件源对象（即触发事件的组件）
 *    - getWhen(): 返回事件发生的时间戳
 * 5. 外部事件处理类 —— ButtonHandler 作为独立的类实现 ActionListener，
 *    将事件处理逻辑与 GUI 代码分离，提高复用性和可维护性。
 * 6. FlowLayout.CENTER —— 创建 FlowLayout 并指定居中对齐。
 */

package chp8_awt_swing.exp8_10;                             // 声明包路径，对应第8章AWT/Swing实验10

import java.awt.FlowLayout;                                 // 导入流式布局管理器
import java.awt.event.ActionEvent;                          // 导入动作事件类
import java.awt.event.ActionListener;                       // 导入动作监听器接口

import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame

public class TestButton {                                   // 定义公开类 TestButton（不继承 JFrame）

    public static void main(String args[ ]) {               // 主入口方法
        JFrame f = new JFrame("Test");                      // 创建 JFrame 窗口对象，标题为 "Test"
        f.setSize(200, 100);                                // 设置窗口宽200像素、高100像素
        f.setLayout(new FlowLayout(FlowLayout.CENTER));     // 设置窗口布局为 FlowLayout，居中对齐
        f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);   // 设定关闭窗口时退出程序

        JButton b = new JButton("Press Me!");               // 创建一个按钮，标题为 "Press Me!"
        b.addActionListener(new ButtonHandler());           // 为按钮注册事件监听器，传入 ButtonHandler 实例
        f.add(b);                                           // 将按钮添加到窗口中
        f.setVisible(true);                                 // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束

// 外部类：处理按钮点击事件，实现 ActionListener 接口
class ButtonHandler implements ActionListener {             // 定义包级私有类（无 public 修饰符）

    public void actionPerformed(ActionEvent e) {            // 实现 ActionListener 接口的唯一方法
        System.out.println("Action occurred");              // 在控制台输出 "Action occurred"（动作发生了）
        System.out.println("Button's label is:" +           // 在控制台输出按钮的标签文字
                e.getActionCommand());                      // getActionCommand() 返回按钮上的文字
    }                                                       // actionPerformed 方法结束

}                                                           // ButtonHandler 类定义结束
