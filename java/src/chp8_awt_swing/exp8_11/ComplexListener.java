/**
 * 【功能说明】
 * 本程序演示一个类同时实现多个事件监听器接口。
 * ComplexListener 类同时实现了三个监听器接口：
 *   1. MouseMotionListener —— 监听鼠标移动和拖拽事件
 *   2. MouseListener —— 监听鼠标进入、退出、点击、按下、释放事件
 *   3. ActionListener —— 监听按钮动作事件
 * 在文本区域中拖拽鼠标时，会实时显示鼠标坐标；
 * 鼠标进入/退出/点击文本区域时也会显示相应信息；
 * 点击"退出"按钮则关闭程序。
 *
 * 【知识点】
 * 1. 多接口实现 —— 一个类可以同时实现多个接口（implements A, B, C），
 *    从而监听多种不同类型的事件。
 * 2. MouseMotionListener —— 鼠标运动监听器，包含两个方法：
 *    - mouseDragged(MouseEvent): 鼠标按键按下并拖拽时触发
 *    - mouseMoved(MouseEvent): 鼠标移动时触发
 * 3. MouseListener —— 鼠标按键监听器，包含5个方法：
 *    - mouseClicked: 鼠标点击时触发
 *    - mousePressed: 鼠标按下时触发
 *    - mouseReleased: 鼠标释放时触发
 *    - mouseEntered: 鼠标进入组件区域时触发
 *    - mouseExited: 鼠标离开组件区域时触发
 * 4. MouseEvent 鼠标事件提供的方法：
 *    - getX() / getY(): 事件发生时的鼠标坐标
 *    - getSource(): 返回事件源组件
 * 5. JTextArea —— 多行文本区域，支持追加文本（append）和换行
 * 6. 事件处理中调用 System.exit(0) 来退出程序
 * 7. 未使用的方法需要保留空实现（接口要求实现所有方法）
 */

package chp8_awt_swing.exp8_11;                             // 声明包路径，对应第8章AWT/Swing实验11

import java.awt.BorderLayout;                               // 导入边界布局管理器
import java.awt.event.ActionEvent;                          // 导入动作事件类
import java.awt.event.ActionListener;                       // 导入动作监听器接口
import java.awt.event.MouseEvent;                           // 导入鼠标事件类
import java.awt.event.MouseListener;                        // 导入鼠标监听器接口
import java.awt.event.MouseMotionListener;                  // 导入鼠标运动监听器接口

import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JLabel;                                  // 导入 Swing 标签类 JLabel
import javax.swing.JTextArea;                               // 导入 Swing 文本区域类

public class ComplexListener implements                     // 定义类，同时实现3个监听器接口
        MouseMotionListener, MouseListener, ActionListener {

    JFrame f;                                               // 声明 JFrame 窗口对象变量
    JTextArea tf;                                           // 声明 JTextArea 文本区域变量（用于显示事件信息）
    JButton bt;                                             // 声明 JButton 按钮变量（用于退出）
    int number = 1;                                         // 计数器，用于给事件序号编号（从1开始）

    public ComplexListener() {                              // 构造方法：初始化所有组件并注册事件监听器
        JLabel label = new JLabel("click and Drag the mouse"); // 创建提示标签，显示"点击并拖拽鼠标"
        f = new JFrame("Complex Listener");                 // 创建窗口，标题为 "Complex Listener"
        tf = new JTextArea();                               // 创建文本区域对象，用于显示事件信息
        bt = new JButton("退出");                            // 创建按钮，文字为"退出"

        tf.addMouseMotionListener(this);                    // 向文本区域注册鼠标运动监听器（this实现）
        tf.addMouseListener(this);                          // 向文本区域注册鼠标监听器（this实现）
        bt.addActionListener(this);                         // 向按钮注册动作监听器（this实现）

        f.add(label, BorderLayout.NORTH);                   // 将标签添加到窗口 NORTH（上方）区域
        f.add(tf, BorderLayout.CENTER);                     // 将文本区域添加到窗口 CENTER（中央）区域
        f.add(bt, BorderLayout.SOUTH);                      // 将退出按钮添加到窗口 SOUTH（下方）区域
        f.setSize(300, 200);                                // 设置窗口宽300像素、高200像素
        f.setVisible(true);                                 // 使窗口可见
    }                                                       // 构造方法结束

    // ======== MouseMotionListener 接口的方法（鼠标运动监听） ========
    public void mouseDragged(MouseEvent e) {                // 鼠标拖拽时触发（按着鼠标键移动）
        String s = number++ + " " + "The mouse Dragged: x= "   // 构造事件信息字符串：序号 + "鼠标拖拽: x=..." + " y=..."
                + e.getX() + " y=" + e.getY() + "\n";      // getX()/getY() 获取鼠标在组件内的坐标
        tf.append(s);                                       // 将事件信息追加到文本区域末尾
    }                                                       // mouseDragged 方法结束

    // ======== MouseListener 接口的方法（鼠标操作监听） ========
    public void mouseEntered(MouseEvent e) {                // 鼠标进入组件区域时触发
        String s = number++ + " " + "The mouse entered" + "\n"; // 构造 "鼠标进入" 信息
        tf.append(s);                                       // 追加到文本区域
    }                                                       // mouseEntered 方法结束

    public void mouseClicked(MouseEvent e) {                // 鼠标点击时触发
        String s = number++ + " " + "The mouse clicked." + "\n"; // 构造 "鼠标点击" 信息
        tf.append(s);                                       // 追加到文本区域
    }                                                       // mouseClicked 方法结束

    public void mouseExited(MouseEvent e) {                 // 鼠标离开组件区域时触发
        String s = number++ + " " + "The mouse exit." + "\n"; // 构造 "鼠标离开" 信息
        tf.append(s);                                       // 追加到文本区域
    }                                                       // mouseExited 方法结束

    // 以下三个方法虽然没有使用，但接口要求必须实现（提供空实现即可）
    public void mouseMoved(MouseEvent e) { }                // MouseMotionListener 的方法：鼠标移动（未使用，空实现）
    public void mouseReleased(MouseEvent e) { }             // MouseListener 的方法：鼠标释放（未使用，空实现）
    public void mousePressed(MouseEvent e) { }              // MouseListener 的方法：鼠标按下（未使用，空实现）

    // ======== ActionListener 接口的方法（按钮动作监听） ========
    public void actionPerformed(ActionEvent e) {            // 按钮被点击时触发
        System.exit(0);                                     // 退出 Java 虚拟机，结束程序
    }                                                       // actionPerformed 方法结束

    public static void main(String args[]) {                // 主入口方法
        ComplexListener two = new ComplexListener();        // 创建 ComplexListener 实例（构造方法自动完成所有初始化）
    }                                                       // main 方法结束

}                                                           // 类定义结束
