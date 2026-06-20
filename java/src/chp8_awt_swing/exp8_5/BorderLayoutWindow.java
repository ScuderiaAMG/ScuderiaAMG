/**
 * 【功能说明】
 * 本程序演示 BorderLayout（边界布局管理器）的使用。
 * BorderLayout 将容器分为5个区域：北(North)、南(South)、东(East)、西(West)、中(Center)。
 * 每个区域最多只能放置一个组件。当窗口尺寸变化时：
 *   - North/South 区域保持原始高度，宽度自适应
 *   - East/West 区域保持原始宽度，高度自适应
 *   - Center 区域在水平和垂直方向都自动伸展填充剩余空间
 *
 * 【知识点】
 * 1. BorderLayout —— 边界布局管理器，JFrame 内容面板的默认布局管理器。
 * 2. 向 BorderLayout 中添加组件时，需要指定区域位置常量：
 *    - "North" 或 BorderLayout.NORTH     —— 上方区域
 *    - "South" 或 BorderLayout.SOUTH     —— 下方区域
 *    - "East" 或 BorderLayout.EAST       —— 右侧区域
 *    - "West" 或 BorderLayout.WEST       —— 左侧区域
 *    - "Center" 或 BorderLayout.CENTER   —— 中央区域（默认）
 * 3. 如果不指定区域位置，组件默认添加到 CENTER 区域，
 *    后添加的组件会覆盖之前添加的（因为每个区域只能放一个组件）。
 * 4. pack() —— 根据组件的首选大小自动调整窗口尺寸。
 */

package chp8_awt_swing.exp8_5;                              // 声明包路径，对应第8章AWT/Swing实验5

import java.awt.BorderLayout;                               // 导入边界布局管理器

import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame

public class BorderLayoutWindow extends JFrame {            // 继承 JFrame 创建自定义窗口类

    public BorderLayoutWindow() {                           // 构造方法：初始化布局并添加组件
        setLayout(new BorderLayout());                      // 将窗口的布局管理器设置为 BorderLayout（虽然 JFrame 默认可省略）

        add(new JButton("North"), "North");                 // 在北方区域添加一个按钮，文字为 "North"
        add(new JButton("South"), "South");                 // 在南方区域添加一个按钮，文字为 "South"
        add(new JButton("East"), "East");                   // 在东方区域添加一个按钮，文字为 "East"
        add(new JButton("West"), "West");                   // 在西方区域添加一个按钮，文字为 "West"
        add(new JButton("Center"), "Center");               // 在中央区域添加一个按钮，文字为 "Center"
    }                                                       // 构造方法结束

    public static void main(String args[]) {                // 主入口方法
        BorderLayoutWindow window = new BorderLayoutWindow(); // 创建自定义窗口对象

        window.setTitle("BorderWindow Application");        // 设置窗口标题
        window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); // 设定关闭窗口时退出程序
        window.pack();                                      // 自动调整窗口大小到适合所有组件
        window.setVisible(true);                            // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束
