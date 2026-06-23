/**
 * 【功能说明】
 * 本程序演示 JTabbedPane（选项卡面板）的使用。
 * JTabbedPane 提供一组带标签的选项卡（Tab），用户点击选项卡标签
 * 即可切换显示对应的面板内容。本程序创建了4个选项卡，
 * 分别显示不同的文本信息（"你好"、"Blah blah"等），
 * 每个选项卡都带有一个图标。同时演示了 ImageIcon 的使用。
 *
 * 【知识点】
 * 1. JTabbedPane —— Swing 的选项卡面板组件，允许多个面板共用同一显示区域，
 *    通过点击标签切换显示内容。常用方法：
 *    - addTab(标题, 图标, 组件, 提示信息): 添加选项卡
 *    - setSelectedIndex(index): 设置当前选中的选项卡索引（从0开始）
 * 2. ImageIcon —— Swing 中用于加载和显示图像的类，
 *    构造函数接收图片文件的路径（支持 GIF、JPEG、PNG 等格式）。
 * 3. JPanel(false) —— JPanel 构造方法的 boolean 参数表示是否使用双缓冲
 *    （double-buffered），false 表示不使用（本例中不是动画场景）。
 * 4. JLabel.CENTER —— 标签的水平对齐方式常量，表示居中对齐。
 * 5. GridLayout(1, 1) —— 1行1列的网格布局，使添加的组件填满整个面板。
 * 6. extends JPanel —— 本类继承 JPanel 而非 JFrame，
 *    这意味着 TabbedPaneDemo 本身是一个面板，可以被嵌入到其他容器中。
 *    在 main 方法中将其添加到 JFrame 的内容面板中。
 * 7. 嵌套布局模式 —— JFrame(BorderLayout) → 内部包含 TabbedPaneDemo(GridLayout) → 内部包含 JTabbedPane。
 */

package chp8_awt_swing.exp8_15;                             // 声明包路径，对应第8章AWT/Swing实验15

import java.awt.BorderLayout;                               // 导入边界布局管理器
import java.awt.Component;                                  // 导入组件基类，用于声明方法返回类型
import java.awt.GridLayout;                                 // 导入网格布局管理器
import java.awt.event.WindowAdapter;                        // 导入窗口事件适配器类
import java.awt.event.WindowEvent;                          // 导入窗口事件类

import javax.swing.ImageIcon;                               // 导入图像图标类（加载图片）
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JLabel;                                  // 导入 Swing 标签类 JLabel
import javax.swing.JPanel;                                  // 导入 Swing 面板类 JPanel
import javax.swing.JTabbedPane;                             // 导入 Swing 选项卡面板类

public class TabbedPaneDemo extends JPanel {                // 继承 JPanel 创建自定义面板类

    public TabbedPaneDemo() {                               // 构造方法：初始化选项卡面板和内容
        ImageIcon icon = new ImageIcon("java/src/chp8_awt_swing/exp8_15/new.gif");
        // ↑ 加载图片文件创建图标对象，路径相对于项目根目录

        JTabbedPane tabbedPane = new JTabbedPane();         // 创建选项卡面板对象

        // 创建第一个选项卡："One"，图标为 icon，内容为"你好"的标签面板，提示信息为 "Does nothing"
        Component panel1 = makeTextPanel("Your mom is a sex slave.");         // 调用辅助方法创建文本显示面板
        tabbedPane.addTab("One", icon, panel1, "Does nothing"); // 添加选项卡（标题、图标、面板、提示）
        tabbedPane.setSelectedIndex(0);                     // 默认选中第一个选项卡（索引从0开始）

        // 创建第二个选项卡："Two"，内容为 "Blah blah"，提示信息为 "Does twice as much nothing"
        Component panel2 = makeTextPanel("Your mom is willing to give me a blowjob and anal sex.");      // 创建文本面板 "Blah blah"
        tabbedPane.addTab("Two", icon, panel2, "Does twice as much nothing"); // 添加选项卡

        // 创建第三个选项卡："Three"，内容为 "Blah blah blah"
        Component panel3 = makeTextPanel("Your mom is willing to be raped by me."); // 创建文本面板
        tabbedPane.addTab("Three", icon, panel3, "Still does nothing"); // 添加选项卡

        // 创建第四个选项卡："Four"，内容为 "Blah blah blah blah"
        Component panel4 = makeTextPanel("I fucked your mom to orgasm with my dick."); // 创建文本面板
        tabbedPane.addTab("Four", icon, panel4, "Does nothing at all"); // 添加选项卡

        // 将选项卡面板添加到当前面板（TabbedPaneDemo）中
        setLayout(new GridLayout(1, 1));                    // 设置当前面板为1行1列网格布局（填满容器）
        add(tabbedPane);                                    // 将选项卡面板添加到当前面板中
    }                                                       // 构造方法结束

    // 辅助方法：创建包含指定文本的 JPanel（用于作为选项卡的内容面板）
    protected Component makeTextPanel(String text) {        // 方法定义，接收文本参数
        JPanel panel = new JPanel(false);                   // 创建 JPanel，关闭双缓冲（false）
        JLabel filler = new JLabel(text);                   // 创建标签，显示指定文本
        filler.setHorizontalAlignment(JLabel.CENTER);       // 设置标签文字水平居中对齐
        panel.setLayout(new GridLayout(1, 1));              // 设置面板为1x1网格（填满整个面板区域）
        panel.add(filler);                                  // 将标签添加到面板中
        return panel;                                       // 返回创建好的面板
    }                                                       // makeTextPanel 方法结束

    public static void main(String[] args) {                // 主入口方法
        JFrame.setDefaultLookAndFeelDecorated(true);        // 让 JFrame 使用 Swing 默认窗口装饰（非系统原生）
        JFrame frame = new JFrame("TabbedPaneDemo");        // 创建 JFrame 窗口，标题为 "TabbedPaneDemo"
        frame.addWindowListener(new WindowAdapter() {       // 注册窗口事件监听器（匿名内部类）
            public void windowClosing(WindowEvent e) {      // 点击关闭按钮时触发
                System.exit(0);                             // 退出 JVM，结束程序
            }                                               // windowClosing 方法结束
        });                                                 // 匿名内部类结束

        frame.getContentPane().add(new TabbedPaneDemo(),    // 将自定义面板（含选项卡）添加到窗口内容面板
                                   BorderLayout.CENTER);    // 放置在 CENTER 区域
        frame.setSize(400, 125);                             // 设置窗口宽400像素、高125像素
        frame.setVisible(true);                             // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束
