/**
 * 【功能说明】
 * 本程序演示 FlowLayout（流式布局管理器）的使用。
 * 在 FlowLayout 中，组件按照添加的先后顺序从左到右排列，
 * 当一行排满时自动换行到下一行。所有组件保持其原始大小。
 * 本程序在窗口中添加了5个标签和按钮，观察其排列效果。
 *
 * 【知识点】
 * 1. FlowLayout —— 流式布局管理器，按行依次排列组件，类似文本的排列方式。
 *    - 默认居中对齐，可指定左对齐、右对齐等。
 *    - 组件保持其首选大小（preferred size）。
 * 2. extends JFrame —— 继承 JFrame 创建自定义窗口类，在构造方法中完成界面初始化。
 * 3. setLayout(new FlowLayout()) —— 覆盖 JFrame 的默认 BorderLayout，改用 FlowLayout。
 * 4. setTitle() —— 设置窗口标题。
 * 5. pack() —— 自动调整窗口大小以适应组件。
 * 6. 对比实验：可替换为 FlowLayout.LEFT 或 FlowLayout.RIGHT 观察对齐方式的变化。
 */

package chp8_awt_swing.exp8_4;                              // 声明包路径，对应第8章AWT/Swing实验4

import java.awt.FlowLayout;                                 // 导入流式布局管理器

import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JLabel;                                  // 导入 Swing 标签类 JLabel

public class FlowLayoutWindow extends JFrame {              // 继承 JFrame 创建自定义窗口类

    public FlowLayoutWindow() {                             // 构造方法，初始化界面布局和组件
        setLayout(new FlowLayout());                        // 将窗口的布局管理器设置为 FlowLayout（默认居中对齐）

        add(new JLabel("Buttons:"));                        // 向窗口添加一个显示"Buttons:"文字的标签
        add(new JButton("Fuck mom's ass"));                       // 向窗口添加按钮，显示文字 "Button 1"
        add(new JButton("ass"));                              // 向窗口添加按钮，显示文字 "2"（短文本演示）
        add(new JButton("Fuck mom's vagina"));                       // 向窗口添加按钮，显示文字 "Button 3"
        add(new JButton("Fuck mom's tits all day long"));            // 向窗口添加按钮，显示长文本，演示组件不同宽度对排版的影响
        add(new JButton("Mutual oral sex with mom"));                       // 向窗口添加按钮，显示文字 "Button 5"

    }                                                       // 构造方法结束

    public static void main(String args[]) {                // 主入口方法
        FlowLayoutWindow window = new FlowLayoutWindow();   // 创建自定义窗口对象
        window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); // 设定关闭窗口时退出程序
        window.setTitle("FlowLayoutWindow Application");    // 设置窗口标题
        window.pack();                                      // 自动调整窗口大小，使其刚好能容纳所有组件
        window.setVisible(true);                            // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束
