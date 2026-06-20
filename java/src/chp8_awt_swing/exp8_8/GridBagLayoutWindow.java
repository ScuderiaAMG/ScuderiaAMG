/**
 * 【功能说明】
 * 本程序演示 GridBagLayout（网格包布局管理器）的使用。
 * GridBagLayout 是 Swing 中最灵活、最强大的布局管理器，
 * 通过 GridBagConstraints 约束对象来控制每个组件的位置、大小和对齐方式。
 * 本程序使用 GridBagLayout 创建了一个包含10个按钮的不规则网格窗口，
 * 演示了 fill、weightx、weighty、gridwidth、gridheight 等关键约束属性的用法。
 *
 * 【知识点】
 * 1. GridBagLayout —— 网格包布局管理器，以网格单元为基础，
 *    但允许组件跨越多行多列，实现复杂的布局效果。
 * 2. GridBagConstraints —— 布局约束类，为每个组件指定放置规则，包括：
 *    - fill: 组件在网格单元中的填充方式（NONE/HORIZONTAL/VERTICAL/BOTH）
 *    - weightx / weighty: 分配额外空间的权重比例
 *    - gridwidth / gridheight: 组件占用的列数/行数
 *      - REMAINDER: 占据剩余所有列/行
 *      - RELATIVE: 占据倒数第二个位置
 *    - gridx / gridy: 组件在网格中的位置（可省略，用 RELATIVE 自动布局）
 * 3. 自定义辅助方法 makebutton() —— 封装按钮创建和约束设置的过程，
 *    避免重复代码，体现"封装"思想。
 * 4. 约束的可变性 —— 同一个 GridBagConstraints 对象可以被重复使用，
 *    每次使用前修改其属性即可影响下一个添加的组件。
 */

package chp8_awt_swing.exp8_8;                              // 声明包路径，对应第8章AWT/Swing实验8

import java.awt.GridBagConstraints;                         // 导入网格包布局约束类
import java.awt.GridBagLayout;                              // 导入网格包布局管理器

import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame

public class GridBagLayoutWindow extends JFrame {           // 继承 JFrame 创建自定义窗口类

    // 辅助方法：根据名称创建按钮，并使用给定的 GridBagConstraints 约束将其添加到布局中
    // 参数：name —— 按钮的文字标签
    //       gridbag —— GridBagLayout 布局管理器对象
    //       c —— GridBagConstraints 约束对象，控制按钮在网格中的位置和大小
    protected void makebutton(String name,                  // 方法定义：接收按钮名称
                              GridBagLayout gridbag,         // 接收布局管理器对象
                              GridBagConstraints c) {        // 接收布局约束对象
        JButton button = new JButton(name);                 // 创建带指定文字的按钮
        gridbag.setConstraints(button, c);                  // 将约束 c 应用到按钮上（设置按钮在网格中的布局参数）
        add(button);                                        // 将按钮添加到当前窗口（JFrame）中
    }                                                       // makebutton 方法结束

    public GridBagLayoutWindow() {                          // 构造方法：初始化布局并添加10个按钮
        GridBagLayout gridbag = new GridBagLayout();        // 创建 GridBagLayout 布局管理器对象
        GridBagConstraints c = new GridBagConstraints();    // 创建 GridBagConstraints 约束对象（默认值初始化）

        setLayout(gridbag);                                 // 将窗口的布局管理器设置为 GridBagLayout

        c.fill = GridBagConstraints.BOTH;                   // 设置填充方式：BOTH 表示组件水平垂直双向拉伸填满网格单元
        c.weightx = 1.0;                                    // 水平权重=1.0，当窗口宽度变大时，水平多余空间全部分配给此组件
        makebutton("Button1", gridbag, c);                  // 添加 Button1：占1列，水平可拉伸
        makebutton("Button2", gridbag, c);                  // 添加 Button2：占1列，水平可拉伸
        makebutton("Button3", gridbag, c);                  // 添加 Button3：占1列，水平可拉伸

        c.gridwidth = GridBagConstraints.REMAINDER;         // 修改约束：组件占据当前行剩余的所有列，自动换行
        makebutton("Button4", gridbag, c);                  // 添加 Button4：占满当前行所有剩余列，换行

        c.weightx = 0.0;                                    // 复位水平权重为0（默认值），不再分配额外的水平空间
        makebutton("Button5", gridbag, c);                  // 添加 Button5：另起一行，gridwidth 仍为 REMAINDER

        c.gridwidth = GridBagConstraints.RELATIVE;          // 修改约束：组件占据当前行倒数第二个位置（后面还有一列）
        makebutton("Button6", gridbag, c);                  // 添加 Button6：占据当前行的倒数第二列

        c.gridwidth = GridBagConstraints.REMAINDER;         // 再次改为占满剩余列
        makebutton("Button7", gridbag, c);                  // 添加 Button7：占据当前行最后一列

        c.gridwidth = 1;                                    // 复位列宽为1（默认值），只占一列
        c.gridheight = 2;                                   // 设置行高为2，即该组件垂直跨越2行
        c.weighty = 1.0;                                    // 垂直权重=1.0，当窗口高度变大时，分配额外垂直空间
        makebutton("Button8", gridbag, c);                  // 添加 Button8：占1列2行，垂直可拉伸

        c.weighty = 0.0;                                    // 复位垂直权重为0（默认值）
        c.gridwidth = GridBagConstraints.REMAINDER;         // 改为占满剩余列
        c.gridheight = 1;                                   // 复位行高为1（默认值），只占一行
        makebutton("Button9", gridbag, c);                  // 添加 Button9：Button8 右侧，占满剩余空间
        makebutton("Button10", gridbag, c);                 // 添加 Button10：另起一行，占满整行
    }                                                       // 构造方法结束

    public static void main(String args[]) {                // 主入口方法
        GridBagLayoutWindow window = new GridBagLayoutWindow(); // 创建自定义窗口对象

        window.setTitle("GridBagLayoutWindow Application"); // 设置窗口标题
        window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); // 设定关闭窗口时退出程序
        window.pack();                                      // 自动调整窗口大小
        window.setVisible(true);                            // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束
