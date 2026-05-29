package chp8_awt_swing.exp8_12;                     // 声明包名，对应第8章 AWT/Swing 实验12

import java.awt.GridBagConstraints;                 // 导入网格包布局的约束类，控制组件在网格中的位置和大小
import java.awt.GridBagLayout;                      // 导入网格包布局管理器，最灵活的 Swing 布局
import java.awt.Insets;                             // 导入内边距类，控制组件四周的留白距离
import java.awt.event.ActionEvent;                  // 导入动作事件类，封装按钮点击等事件信息
import java.awt.event.ActionListener;               // 导入动作监听器接口，实现它才能响应按钮点击
import java.awt.event.WindowAdapter;                // 导入窗口适配器类，窗口事件的空实现，只需重写关心的方法
import java.awt.event.WindowEvent;                  // 导入窗口事件类，封装窗口打开、关闭等事件信息

import javax.swing.JButton;                         // 导入 Swing 按钮组件
import javax.swing.JFrame;                          // 导入 Swing 顶层窗口容器
import javax.swing.JLabel;                          // 导入 Swing 标签组件，显示文本
import javax.swing.JTextArea;                       // 导入 Swing 多行文本区组件

public class MultiListener extends JFrame implements ActionListener {
    // ↑ 类名 MultiListener = Multi(多个) + Listener(监听器)
    // ↑ extends JFrame：本类是一个窗口
    // ↑ implements ActionListener：本类自己也是一个按钮监听器

    JTextArea topTextArea;                           // 上方文本区，显示"监听器"听到的内容（只读）
    JTextArea bottomTextArea;                        // 下方文本区，显示"偷听者"听到的内容（只读）
    JButton button1, button2;                        // 声明两个按钮：按钮1和按钮2

    public MultiListener(String s) {                 // 构造方法，参数 s 是窗口标题
        super(s);                                    // 调用父类 JFrame 构造，设置窗口标题

        JLabel l = null;                             // 临时标签变量，复用于创建多个标签
        GridBagLayout gridbag = new GridBagLayout(); // 创建网格包布局管理器对象
        GridBagConstraints c = new GridBagConstraints(); // 创建布局约束对象，控制每个组件怎么放
        setLayout(gridbag);                          // 将窗口的布局管理器设为 GridBagLayout

        c.fill = GridBagConstraints.BOTH;            // 组件在格子里水平和垂直两个方向都拉伸填满
        c.gridwidth = GridBagConstraints.REMAINDER;  // 组件占满当前行剩余列，下一个组件自动换行

        l = new JLabel("监听器听到的:");               // 创建标签："监听器听到的:"
        gridbag.setConstraints(l, c);                // 将约束 c 应用到标签 l 上（占整行、双向填满）
        add(l);                                      // 把标签添加到窗口（第1行）

        c.weighty = 1.0;                             // 垂直权重=1.0，窗口拉大时多余垂直空间分给这个组件
        topTextArea = new JTextArea(5, 20);          // 创建文本区：5行高、20列宽
        topTextArea.setEditable(false);              // 设为只读，用户不能在文本区里打字
        gridbag.setConstraints(topTextArea, c);      // topTextArea 也占整行、垂直方向可拉伸
        add(topTextArea);                            // 添加到窗口（第2行）

        c.weightx = 0.0;                             // 水平权重清零（对整行组件无实际影响）
        c.weighty = 0.0;                             // 垂直权重清零，标签不需要拉伸
        l = new JLabel("偷听者听到的:");               // 复用 l 变量，创建第二个标签
        gridbag.setConstraints(l, c);                // 应用约束
        add(l);                                      // 添加到窗口（第3行）

        c.weighty = 1.0;                             // 垂直权重重新设为1.0，让第二个文本区也能拉伸
        bottomTextArea = new JTextArea(5, 20);       // 创建第二个文本区：5行高、20列宽
        bottomTextArea.setEditable(false);           // 同样设为只读
        gridbag.setConstraints(bottomTextArea, c);   // 应用约束
        add(bottomTextArea);                         // 添加到窗口（第4行）

        c.weightx = 1.0;                             // 水平权重=1.0，窗口拉宽时多余水平空间分给按钮
        c.weighty = 0.0;                             // 垂直权重清零，按钮不需要垂直拉伸
        c.gridwidth = 1;                             // 列宽=1，按钮1只占一个格子
        c.insets = new Insets(10, 10, 0, 10);        // 内边距：上10 左10 下0 右10（像素），让按钮不贴边
        button1 = new JButton("啦 啦 啦");            // 创建按钮1，文字为"啦 啦 啦"
        gridbag.setConstraints(button1, c);          // 应用约束：占1格、有内边距
        add(button1);                                // 添加到窗口（第5行第1格）

        c.gridwidth = GridBagConstraints.REMAINDER;  // 按钮2占满剩下的格子，它是当前行最后一个
        button2 = new JButton("你别说话!");           // 创建按钮2，文字为"你别说话!"
        gridbag.setConstraints(button2, c);          // 应用约束
        add(button2);                                // 添加到窗口（第5行第2格，也是本行末尾）

        // ========== 以下为事件监听器注册部分（本程序的核心） ==========

        // 注册1：button1 的点击事件由 MultiListener 自己监听
        button1.addActionListener(this);
        // 注册2：button2 的点击事件由 MultiListener 自己监听
        button2.addActionListener(this);
        // 注册3：button2 再额外注册一个 Eavesdropper（偷听者）监听器
        //        此时 button2 有两个监听器，点击时会依次触发两个 actionPerformed
        button2.addActionListener(new Eavesdropper());

        // 注册4：窗口关闭事件 → 匿名内部类继承 WindowAdapter
        //        WindowAdapter 实现了 WindowListener 接口的7个方法（全为空实现）
        //        这里只重写 windowClosing 一个方法，不用写其他6个
        addWindowListener(new WindowAdapter() {
            public void windowClosing(WindowEvent e) { // 用户点击窗口右上角 X 时触发
                System.exit(0);                        // 退出 Java 虚拟机，彻底关闭程序
            }
        });

        pack();                                      // 自动计算所有组件的最佳大小并调整窗口
        setVisible(true);                            // 让窗口可见（默认不可见）
    }

    // ========== MultiListener 自己的事件响应（第1个监听器） ==========
    public void actionPerformed(ActionEvent e) {     // 实现 ActionListener 接口的方法
        // e.getActionCommand() 返回按钮上的文字（默认 ActionCommand = 按钮文本）
        // append() 在文本区末尾追加内容，"\n" 是换行符
        topTextArea.append(e.getActionCommand() + "\n"); // 在上方文本区显示按钮文字
    }

    // ========== 内部类：Eavesdropper（第2个监听器） ==========
    // class 前没有 public，是包级私有内部类，只在 MultiListener 内部使用
    class Eavesdropper implements ActionListener {   // Eavesdropper = 偷听者/窃听者，比喻它在"偷听"按钮事件
        public void actionPerformed(ActionEvent e) { // 实现 ActionListener 接口的方法
            // 收到事件后在下方的文本区显示，前面加上 "OK," 前缀以示区别
            bottomTextArea.append("OK," + e.getActionCommand() + "\n");
        }
    }

    // ========== 程序入口 ==========
    public static void main(String[] args) {         // Java 程序主入口
        // 创建 MultiListener 对象，窗口标题为 "MultiListener example"
        // 构造方法里完成了所有初始化：布局、注册监听器、显示窗口
        MultiListener m = new MultiListener("MultiListener example");
    }
}
