/**
 * 【功能说明】
 * 本程序演示 CardLayout（卡片布局管理器）的使用。
 * CardLayout 将多个组件（通常是 JPanel）像一叠卡片一样叠放，
 * 每次只显示其中一张卡片，通过方法调用来切换显示哪张卡片。
 * 本程序包含两张"卡片"：
 *   卡片1 —— 包含3个按钮的面板
 *   卡片2 —— 包含一个文本输入框的面板
 * 单击"卡片切换"按钮可在两张卡片之间切换。
 * 同时演示了 ActionListener 事件监听接口的实现。
 *
 * 【知识点】
 * 1. CardLayout —— 卡片布局管理器，同一时刻只显示一个组件。
 *    常用方法：first()、last()、next()、previous()、show(容器, 名称)。
 * 2. implements ActionListener —— 通过让窗口类实现 ActionListener 接口，
 *    使窗口本身成为按钮的事件监听器，在 actionPerformed 中处理点击事件。
 * 3. BorderLayout + CardLayout 嵌套 —— 外部窗口使用 BorderLayout，
 *    内部卡片面板使用 CardLayout，实现切换按钮在上方、卡片在中央的效果。
 * 4. JTextField —— Swing 文本输入框组件，允许用户输入单行文本。
 * 5. add("名称", 组件) —— 向 CardLayout 容器添加组件时指定一个字符串名称，
 *    后续通过 show() 方法可用该名称切换到对应组件。
 * 6. this 作为监听器 —— 本类实现了 ActionListener 接口，
 *    所以 this 可以直接作为 addActionListener() 的参数。
 */

package chp8_awt_swing.exp8_7;                              // 声明包路径，对应第8章AWT/Swing实验7

import java.awt.BorderLayout;                               // 导入边界布局管理器
import java.awt.CardLayout;                                 // 导入卡片布局管理器
import java.awt.event.ActionEvent;                          // 导入动作事件类
import java.awt.event.ActionListener;                       // 导入动作监听器接口

import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JPanel;                                  // 导入 Swing 面板类 JPanel
import javax.swing.JTextField;                              // 导入 Swing 文本输入框类

public class CardLayoutWindow extends JFrame implements ActionListener {
    // ↑ 继承 JFrame 成为窗口；实现 ActionListener 接口，使本类能处理按钮点击事件

    JPanel cards;                                           // 声明卡片面板（存放多张卡片的容器）
    CardLayout CLayout = new CardLayout();                  // 创建卡片布局管理器对象

    public CardLayoutWindow() {                             // 构造方法：初始化窗口布局和组件
        setLayout(new BorderLayout());                      // 将窗口的主布局设置为 BorderLayout

        // 创建用于放置"卡片切换"按钮的面板，添加到窗口的 NORTH 区域
        JPanel cp = new JPanel();                           // 创建一个 JPanel 面板
        JButton bt = new JButton("卡片切换");               // 创建一个按钮，文字为"卡片切换"
        bt.addActionListener(this);                         // 为按钮注册事件监听器（this 指向本类实例）
        cp.add(bt);                                         // 将按钮添加到面板 cp 中
        add("North", cp);                                   // 将面板 cp 添加到窗口的 NORTH（上方）区域

        // 创建存放多张"卡片"的面板，使用 CardLayout 布局
        cards = new JPanel();                               // 创建卡片容器面板
        cards.setLayout(CLayout);                           // 将 cards 的布局管理器设为 CardLayout

        // 创建第一张卡片：包含3个按钮的面板
        JPanel p1 = new JPanel();                           // 创建面板 p1
        p1.add(new JButton("Button 1"));                    // 向 p1 添加按钮 "Button 1"
        p1.add(new JButton("Button 2"));                    // 向 p1 添加按钮 "Button 2"
        p1.add(new JButton("Button 3"));                    // 向 p1 添加按钮 "Button 3"

        // 创建第二张卡片：包含文本输入框的面板
        JPanel p2 = new JPanel();                           // 创建面板 p2
        p2.add(new JTextField("TextField", 20));            // 向 p2 添加文本框，初始文本"TextField"，宽度20列

        // 将两张卡片添加到卡片容器中，并指定每张卡片的名称
        cards.add("Panel with Buttons", p1);                // 卡片名称为 "Panel with Buttons"，对应 p1
        cards.add("Panel with TextField", p2);              // 卡片名称为 "Panel with TextField"，对应 p2

        // 将卡片容器添加到窗口的 CENTER（中央）区域
        add("Center", cards);                               // cards 面板位于窗口中央
    }                                                       // 构造方法结束

    // 响应"卡片切换"按钮的点击事件
    public void actionPerformed(ActionEvent e) {            // 实现 ActionListener 接口的方法
        CLayout.next(cards);                                // 切换到 cards 中的下一张卡片
    }                                                       // actionPerformed 方法结束

    public static void main(String args[]) {                // 主入口方法
        CardLayoutWindow window = new CardLayoutWindow();   // 创建自定义窗口对象

        window.setTitle("CardWindow Application");          // 设置窗口标题
        window.pack();                                      // 自动调整窗口大小
        window.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE); // 设定关闭窗口时退出程序
        window.setVisible(true);                            // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束
