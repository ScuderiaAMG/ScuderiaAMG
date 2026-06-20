/**
 * 【功能说明】
 * 本程序演示 GridLayout（网格布局管理器）的使用。
 * GridLayout 以规则的网格形式排列组件，每个网格的大小完全相同。
 * 当窗口尺寸变化时，所有网格的大小会均匀地按比例调整。
 * 本程序创建了一个2列的网格窗口，包含6个按钮。
 *
 * 【知识点】
 * 1. GridLayout(rows, cols) —— 网格布局管理器。
 *    - rows: 行数，cols: 列数。
 *    - 如果 rows 为0，则行数根据组件数量自动计算（cols 固定）。
 *    - 反之如果 cols 为0，则列数自动计算。
 *    - 所有网格单元大小完全相等。
 * 2. GridLayout(0, 2) —— 固定2列，行数自动根据组件数量决定。
 *    例如有6个组件，则自动计算为3行2列。
 * 3. 组件按"先行后列"的顺序排列：先填充第1行的各列，再填充第2行，依此类推。
 * 4. 相比 FlowLayout，GridLayout 会强制拉伸所有组件填满整个网格单元。
 * 5. pack() 会依据每个组件的首选大小计算出最合适的窗口尺寸。
 */

package chp8_awt_swing.exp8_6;                              // 声明包路径，对应第8章AWT/Swing实验6

import java.awt.GridLayout;                                 // 导入网格布局管理器

import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame

public class GridLayoutWindow extends JFrame {              // 继承 JFrame 创建自定义窗口类

    public GridLayoutWindow() {                             // 构造方法：初始化布局并添加组件
        setLayout(new GridLayout(0, 2));                    // 设置布局为网格布局，固定2列，行数自动计算

        add(new JButton("Button 1"));                       // 第1行第1列：添加按钮 "Button 1"
        add(new JButton("2"));                              // 第1行第2列：添加按钮 "2"（短文本）
        add(new JButton("Button 3"));                       // 第2行第1列：添加按钮 "Button 3"
        add(new JButton("Long-Named Button 4"));            // 第2行第2列：添加长文本按钮，演示网格单元强制等宽效果
        add(new JButton("Button 5"));                       // 第3行第1列：添加按钮 "Button 5"
        add(new JButton("6"));                              // 第3行第2列：添加按钮 "6"
    }                                                       // 构造方法结束

    public static void main(String args[]) {                // 主入口方法
        GridLayoutWindow window = new GridLayoutWindow();   // 创建自定义窗口对象

        window.setTitle("GridWindow Application");          // 设置窗口标题
        window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); // 设定关闭窗口时退出程序
        window.pack();                                      // 自动调整窗口大小
        window.setVisible(true);                            // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束
