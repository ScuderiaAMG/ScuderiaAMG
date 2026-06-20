/**
 * 【功能说明】
 * 本程序演示 JFrame 的基本使用，包括：
 *   1. 设置窗口使用默认装饰（setDefaultLookAndFeelDecorated）
 *   2. 创建一个带标题的 JFrame 窗口
 *   3. 使用 BorderLayout 布局管理器将组件放置到窗口中央
 *   4. 通过 pack() 自动调整窗口大小以适应组件
 *
 * 【知识点】
 * 1. JFrame.setDefaultLookAndFeelDecorated(true) —— 让 JFrame 使用 Swing 提供的默认窗口装饰
 *    （边框、标题栏等），而非操作系统原生的装饰。
 * 2. BorderLayout —— JFrame 内容面板的默认布局管理器，将容器分为 NORTH/SOUTH/WEST/EAST/CENTER 五个区域。
 * 3. Dimension —— 表示二维尺寸的类，常用于设置组件的首选大小（preferred size）。
 * 4. pack() —— 根据组件的最佳大小自动调整窗口尺寸，替代手动 setSize()。
 * 5. UIManager.setLookAndFeel() —— （被注释掉）Swing 的外观（Look&Feel）切换方法，可换用不同风格。
 */

package chp8_awt_swing.exp8_2;                              // 声明包路径，对应第8章AWT/Swing实验2

import java.awt.BorderLayout;                               // 导入边界布局管理器
import java.awt.Dimension;                                  // 导入尺寸类，用于设置组件的首选大小

//import java.awt.event.*;                                  // （已注释）导入 AWT 事件包，本示例中未直接使用
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JLabel;                                  // 导入 Swing 标签类 JLabel

public class JFrameDemo {                                   // 定义公开类 JFrameDemo

    public static void main(String s[]) throws Exception{   // 主入口方法；throws Exception 允许抛出异常而不在本方法内处理

        // 指定使用当前的 Look&Feel 装饰窗口。可用于在创建窗口前设定外观风格。
        // System.out.println(UIManager.getCrossPlatformLookAndFeelClassName());   // （注释）输出跨平台外观类的完整类名
        // UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());    // （注释）设为系统原生外观（如 Windows 风格）
        // UIManager.setLookAndFeel("javax.swing.plaf.metal.MetalLookAndFeel");    // （注释）设为 Metal 外观（Java 默认跨平台风格）
        // UIManager.setLookAndFeel("com.sun.java.swing.plaf.windows.WindowsLookAndFeel"); // （注释）设为 Windows 外观
        // UIManager.setLookAndFeel("com.sun.java.swing.plaf.mac.MacLookAndFeel"); // （注释）设为 Mac 外观

        JFrame.setDefaultLookAndFeelDecorated(true);        // 让 JFrame 使用 Swing 提供的默认窗口装饰（而非系统原生）

        // 设定窗口标题并设置关闭窗口时的操作
        JFrame frame = new JFrame("JFrameDemo");            // 创建一个 JFrame 窗口对象，标题为 "JFrameDemo"
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);// 点击关闭按钮时退出应用程序

        // 创建一个 JLabel（空标签）并添加到内容面板的中央区域
        JLabel emptyLabel = new JLabel("");                 // 创建一个空文本的 JLabel 对象
        emptyLabel.setPreferredSize(new Dimension(1750, 1000)); // 设置标签的首选大小为宽1750、高1000像素
        frame.getContentPane().add(emptyLabel, BorderLayout.CENTER); // 将空标签添加到内容面板的 CENTER 区域

        // 显示窗口
        frame.pack();                                       // 自动调整窗口大小，使其恰好容纳所有组件的首选大小
        frame.setVisible(true);                             // 使窗口可见
    }                                                       // main 方法结束
}                                                           // 类定义结束
