/**
 * 【功能说明】
 * 本程序演示 JFrame 与 JPanel 的组合使用，以及如何：
 *   1. 继承 JFrame 创建自定义窗口类
 *   2. 创建 JPanel 面板并设置背景颜色
 *   3. 使用 GridLayout 网格布局管理器将按钮排列在面板中
 *   4. 通过 setContentPane() 将面板设置为窗口的内容面板
 *
 * 【知识点】
 * 1. extends JFrame —— 通过继承 JFrame 创建自定义窗口类，可以直接使用 JFrame 的所有功能。
 * 2. JPanel —— Swing 的通用容器面板，用于组织和管理组件的布局。
 * 3. setBackground(Color) —— 设置组件的背景颜色（Color 类提供了预定义颜色常量）。
 * 4. GridLayout(rows, cols) —— 网格布局管理器，以行×列的网格形式排列组件。
 * 5. setContentPane() —— 替换 JFrame 的默认内容面板为自定义面板。
 * 6. super(str) —— 调用父类 JFrame 的构造方法，设置窗口标题。
 */

package chp8_awt_swing.exp8_3;                              // 声明包路径，对应第8章AWT/Swing实验3

import java.awt.Color;                                      // 导入颜色类，用于设置组件的背景/前景色
import java.awt.GridLayout;                                 // 导入网格布局管理器

import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JPanel;                                  // 导入 Swing 面板类 JPanel

public class FrameWithPanel extends JFrame {                // 通过继承 JFrame 创建自定义窗口类

    public static void main(String args[ ]) throws Exception{ // 主入口方法，throws Exception 允许抛出异常
        FrameWithPanel fr = new FrameWithPanel("Hello !");  // 创建自定义窗口对象，标题为 "Hello !"
        fr.setSize(200, 200);                               // 设置窗口宽度200像素，高度200像素
        fr.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);  // 设定点击关闭按钮时退出程序

        JPanel pan = new JPanel();                          // 创建一个 JPanel 面板对象
        pan.setSize(200, 100);                              // 设置面板大小为宽200、高100像素
        pan.setBackground(Color.yellow);                    // 设置面板背景色为黄色
        pan.setLayout(new GridLayout(2, 1));                // 设置面板为2行1列的网格布局
        pan.add(new JButton("确定"));                        // 向面板添加一个显示"确定"文字的按钮

        fr.setContentPane(pan);                             // 将面板设置为窗口的内容面板（替换默认的）
        fr.setVisible(true);                                // 显示窗口
    }                                                       // main 方法结束

    public FrameWithPanel(String str) {                     // 构造方法，参数 str 为窗口标题
        super(str);                                         // 调用父类 JFrame(String) 构造方法，设置标题
    }                                                       // 构造方法结束

}                                                           // 类定义结束
