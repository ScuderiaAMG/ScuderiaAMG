/**
 * 【功能说明】
 * 本程序演示 Swing 事件监听器的高级特性 —— 多个监听器。
 * 核心概念：一个事件源（按钮）可以注册多个监听器，点击时所有监听器依次被调用。
 * 本程序中有两个按钮：
 *   按钮1 "啦 啦 啦" —— 只被 MultiListener（主监听器）监听
 *   按钮2 "你别说话!" —— 被两个监听器同时监听：MultiListener + Eavesdropper（内部类偷听者）
 * 两个文本区分别显示"主监听器"和"偷听者"收到的消息，对比观察多监听器效果。
 * 布局采用 GridBagLayout 实现精细控制。
 *
 * 【知识点】
 * 1. 多监听器 —— Swing 允许为一个组件注册多个监听器，
 *    事件触发时所有注册的监听器会依次被调用。
 * 2. 内部类（Inner Class） —— 在类内部定义的类 Eavesdropper，
 *    可以访问外部类的私有成员变量（bottomTextArea）。
 * 3. GridBagLayout 精细布局 —— 使用 GridBagConstraints 控制：
 *    - fill: 填充方向（BOTH = 双向填充）
 *    - weightx / weighty: 空间分配权重
 *    - gridwidth: 跨列数（REMAINDER = 占满剩余列）
 *    - insets: 组件边距
 * 4. WindowAdapter 匿名内部类 —— 简便的窗口关闭事件处理方式，
 *    只需重写 windowClosing 一个方法。
 * 5. setEditable(false) —— 将文本区域设为只读，用户不能编辑但可以显示内容。
 * 6. getActionCommand() —— 获取按钮的"动作命令"字符串，默认为按钮文本。
 * 7. javadoc 生成 —— 已生成的文档在 index.html 文件中。
 */

package chp8_awt_swing.exp8_12;                             // 声明包路径，对应第8章AWT/Swing实验12

import java.awt.GridBagConstraints;                         // 导入网格包布局约束类
import java.awt.GridBagLayout;                              // 导入网格包布局管理器
import java.awt.Insets;                                     // 导入内边距类，控制组件四周的留白距离
import java.awt.event.ActionEvent;                          // 导入动作事件类
import java.awt.event.ActionListener;                       // 导入动作监听器接口
import java.awt.event.WindowAdapter;                        // 导入窗口事件适配器类
import java.awt.event.WindowEvent;                          // 导入窗口事件类

import javax.swing.JButton;                                 // 导入 Swing 按钮组件
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口容器
import javax.swing.JLabel;                                  // 导入 Swing 标签组件
import javax.swing.JTextArea;                               // 导入 Swing 多行文本区域组件

public class MultiListener_mimofixed extends JFrame implements ActionListener {
    // ↑ 继承 JFrame 成为窗口；实现 ActionListener 接口，使本类自己也能处理按钮点击事件

    JTextArea topTextArea;                                  // 上方文本区：显示"主监听器"收到的按钮文字
    JTextArea bottomTextArea;                               // 下方文本区：显示"偷听者"收到的按钮文字
    JButton button1, button2;                               // 声明两个按钮对象：button1 和 button2

    public MultiListener_mimofixed(String s) {                        // 构造方法，参数 s 为窗口标题
        super(s);                                           // 调用父类 JFrame 的构造方法，设置窗口标题

        JLabel l = null;                                    // 临时标签变量，在后续代码中复用于创建多个标签
        GridBagLayout gridbag = new GridBagLayout();         // 创建 GridBagLayout 布局管理器对象
        GridBagConstraints c = new GridBagConstraints();     // 创建 GridBagConstraints 约束对象
        setLayout(gridbag);                                 // 将窗口的布局管理器设为 GridBagLayout

        c.fill = GridBagConstraints.BOTH;                   // 设置填充方式：BOTH = 水平+垂直双向拉伸填满网格
        c.gridwidth = GridBagConstraints.REMAINDER;         // 设置跨列数：占满当前行剩余所有列，自动换行

        l = new JLabel("监听器听到的:");                      // 创建标签，文字提示"监听器听到的:"
        gridbag.setConstraints(l, c);                       // 将当前约束 c 应用到标签 l 上（占整行，双向填充）
        add(l);                                             // 将标签添加到窗口中（第1行）

        c.weighty = 1.0;                                    // 设置垂直权重=1.0，窗口放大时垂直多余空间分配给此组件
        topTextArea = new JTextArea(5, 20);                 // 创建文本区：5行高、20列宽
        topTextArea.setEditable(false);                     // 设为只读（用户无法编辑，仅供查看）
        gridbag.setConstraints(topTextArea, c);             // 将当前约束应用到 topTextArea
        add(topTextArea);                                   // 添加到窗口（第2行）

        c.weightx = 0.0;                                    // 水平权重清零（对整行组件无实际影响，但恢复默认值）
        c.weighty = 0.0;                                    // 垂直权重清零，标签区域不需要额外空间
        l = new JLabel("偷听者听到的:");                      // 复用 l 变量，创建第二个标签，提示"偷听者听到的:"
        gridbag.setConstraints(l, c);                       // 应用约束
        add(l);                                             // 添加到窗口（第3行）

        c.weighty = 1.0;                                    // 再次设置垂直权重=1.0，让第二个文本区也能拉伸
        bottomTextArea = new JTextArea(5, 20);              // 创建第二个文本区：5行高、20列宽
        bottomTextArea.setEditable(false);                  // 同样设为只读
        gridbag.setConstraints(bottomTextArea, c);          // 应用约束
        add(bottomTextArea);                                // 添加到窗口（第4行）

        c.weightx = 1.0;                                    // 水平权重=1.0，窗口拉宽时水平多余空间分给按钮
        c.weighty = 0.0;                                    // 垂直权重清零，按钮不需要垂直拉伸
        c.gridwidth = 1;                                    // 设置按钮1只占1个网格列
        c.insets = new Insets(10, 10, 0, 10);               // 设置按钮的外边距：上10 左10 下0 右10 像素
        button1 = new JButton("啦 啦 啦");                   // 创建按钮1，文字为"啦 啦 啦"
        gridbag.setConstraints(button1, c);                 // 应用约束：占1列，四周留边距
        add(button1);                                       // 添加到窗口（第5行第1列）

        c.gridwidth = GridBagConstraints.REMAINDER;         // 按钮2占满当前行剩余所有列（即第2列到行尾）
        button2 = new JButton("你别说话!");                  // 创建按钮2，文字为"你别说话!"
        gridbag.setConstraints(button2, c);                 // 应用约束
        add(button2);                                       // 添加到窗口（第5行第2列，也是本行末尾）

        // ========== 事件监听器注册（本程序的核心教学点） ==========

        // 注册1：button1 只被 MultiListener（主监听器）监听
        button1.addActionListener(this);
        // 注册2：button2 也被 MultiListener（主监听器）监听
        button2.addActionListener(this);
        // 注册3：button2 额外再注册一个 Eavesdropper（偷听者）监听器
        //        现在 button2 有2个监听器！点击 button2 时会依次触发两个 actionPerformed 方法
        button2.addActionListener(new Eavesdropper());

        // 注册4：窗口关闭事件 —— 使用匿名内部类继承 WindowAdapter
        //        WindowAdapter 实现了 WindowListener 接口的7个方法（全为空实现）
        //        只需重写 windowClosing 方法，无需实现其他6个无用的方法
        addWindowListener(new WindowAdapter() {             // 创建匿名内部类继承 WindowAdapter
            public void windowClosing(WindowEvent e) {      // 用户点击窗口右上角关闭按钮时触发
                System.exit(0);                             // 退出 Java 虚拟机，彻底结束程序
            }                                               // windowClosing 方法结束
        });                                                 // 匿名内部类结束

        pack();                                             // 自动计算所有组件的最佳大小，调整窗口尺寸
        setVisible(true);                                   // 使窗口可见
    }                                                       // 构造方法结束

    // ========== MultiListener 自己的事件响应方法（第1个监听器） ==========
    public void actionPerformed(ActionEvent e) {            // 实现 ActionListener 接口的方法
        // getActionCommand() 返回按钮上的文字（默认 ActionCommand = 按钮的文本内容）
        // append() 在文本区域末尾追加内容（不会覆盖已有文本）
        topTextArea.append(e.getActionCommand() + "\n");    // 将按钮文字追加到上方文本区并换行
    }                                                       // actionPerformed 方法结束

    // ========== 内部类：Eavesdropper（第2个监听器，即"偷听者"） ==========
    class Eavesdropper implements ActionListener {          // 定义内部类实现 ActionListener 接口
        public void actionPerformed(ActionEvent e) {        // 实现 actionPerformed 方法
            // 收到事件后，在下方文本区显示 "OK, 按钮文字"
            // Eavesdropper 能直接访问外部类的 bottomTextArea 私有成员（内部类特性）
            bottomTextArea.append("OK," + e.getActionCommand() + "\n");
        }                                                   // actionPerformed 方法结束
    }                                                       // Eavesdropper 内部类定义结束

    // ========== 程序入口 ==========
    public static void main(String[] args) {                // Java 程序的主入口方法
        // 创建 MultiListener 对象，窗口标题设为 "MultiListener example"
        // 构造方法中完成了所有初始化：组件布局、注册监听器、显示窗口
        MultiListener_mimofixed m = new MultiListener_mimofixed("MultiListener example");
        System.out.println("MultiListener created: " + m); // 使用m变量，消除未使用变量警告
    }                                                       // main 方法结束

}                                                           // 类定义结束
