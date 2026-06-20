/**
 * 【功能说明】
 * 本程序是 Swing 框架的入门示例 —— "Hello World" 程序。
 * 它创建了一个简单的 Swing 窗口，窗口中显示 "Hello World!" 标签。
 * 通过这个最简示例，展示 Swing GUI 程序的基本骨架：
 *   创建 JFrame → 添加组件 → 设置关闭操作 → 设置大小 → 显示窗口
 *
 * 【知识点】
 * 1. javax.swing.JFrame —— Swing 的顶层窗口容器，所有 Swing GUI 程序的基础。
 * 2. javax.swing.JLabel  —— 显示文本或图标的标签组件，不可编辑。
 * 3. getContentPane()   —— 获取 JFrame 的内容面板(ContentPane)，所有组件应添加到内容面板中。
 * 4. setDefaultCloseOperation() —— 设定点击窗口关闭按钮时的默认行为。
 *    JFrame.EXIT_ON_CLOSE 表示退出应用程序。
 * 5. setSize()  —— 设置窗口的宽度和高度（像素）。
 * 6. setVisible(true) —— 使窗口可见，默认 JFrame 创建后是不可见的。
 */

package chp8_awt_swing.exp8_1;                              // 声明包路径，对应第8章AWT/Swing实验1

import javax.swing.JFrame;                                  // 导入 Swing 的顶层窗口类 JFrame
import javax.swing.JLabel;                                  // 导入 Swing 的标签类 JLabel
//import java.awt.event.*;                                  // （已注释）导入 AWT 事件包，本示例中未使用

public class HelloWorldSwing {                              // 定义公开类 HelloWorldSwing

    public static void main(String[] args) {                // Java 程序的主入口方法
        JFrame frame = new JFrame("HelloWorldSwing");       // 创建一个 JFrame 窗口对象，标题为 "HelloWorldSwing"
        final JLabel label = new JLabel("Hello World!");    // 创建一个 JLabel 标签对象，显示文本 "Hello World!"；final 确保引用不变
        frame.getContentPane().add(label);                  // 获取窗口的内容面板(ContentPane)，并将标签添加到其中
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);// 设定关闭窗口时退出应用程序（否则窗口只是隐藏，进程仍在运行）
        frame.setSize(2000, 700);                           // 设置窗口的宽为2000像素，高为700像素
        frame.setVisible(true);                             // 显示窗口（JFrame 创建后默认不可见，必须调用此方法）
    }                                                       // main 方法结束

}                                                           // 类定义结束
