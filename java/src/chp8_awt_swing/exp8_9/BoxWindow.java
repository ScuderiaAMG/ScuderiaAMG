/**
 * 【功能说明】
 * 本程序演示 BoxLayout（盒式布局管理器）的使用。
 * BoxLayout 将组件沿水平（X_AXIS）或垂直（Y_AXIS）方向依次排列。
 * 与 GridLayout 不同，BoxLayout 不强制所有组件大小相同，
 * 每个组件保持自己的首选大小。
 * 本程序使用 Y_AXIS（垂直排列）展示了5个按钮从上到下的排列效果，
 * 同时演示了 WindowAdapter 窗口适配器处理窗口关闭事件。
 *
 * 【知识点】
 * 1. BoxLayout —— 盒式布局管理器，沿单一方向（水平或垂直）排列组件。
 *    - BoxLayout.X_AXIS: 水平排列
 *    - BoxLayout.Y_AXIS: 垂直排列
 * 2. setAlignmentX(Component.CENTER_ALIGNMENT) —— 设置组件在水平方向上的对齐方式，
 *    CENTER_ALIGNMENT 表示居中对齐，其他还有 LEFT_ALIGNMENT、RIGHT_ALIGNMENT 等。
 * 3. Container —— 所有 Swing 容器的父接口，getContentPane() 返回的就是 Container 对象。
 * 4. WindowAdapter —— 窗口事件适配器，实现了 WindowListener 接口的所有方法（空实现），
 *    只需要重写关心的方法（如 windowClosing），无需实现所有7个方法。
 * 5. 匿名内部类 —— new WindowAdapter() { ... } 创建了一个继承 WindowAdapter 的匿名子类，
 *    在类体内重写 windowClosing 方法，实现窗口关闭处理。
 * 6. System.exit(0) —— 终止当前运行的 Java 虚拟机，参数0表示正常退出。
 */

package chp8_awt_swing.exp8_9;                              // 声明包路径，对应第8章AWT/Swing实验9

import java.awt.Component;                                  // 导入 Component 类，用于 CENTER_ALIGNMENT 常量
import java.awt.Container;                                  // 导入 Container 类，所有容器的父接口
import java.awt.event.WindowAdapter;                        // 导入窗口事件适配器类
import java.awt.event.WindowEvent;                          // 导入窗口事件类

import javax.swing.BoxLayout;                               // 导入盒式布局管理器
import javax.swing.JButton;                                 // 导入 Swing 按钮类
import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame

public class BoxWindow extends JFrame {                     // 继承 JFrame 创建自定义窗口类

    public BoxWindow() {                                    // 构造方法：初始化布局并添加组件
        Container contentPane = getContentPane();            // 获取窗口的内容面板（Container 类型）
        contentPane.setLayout(new BoxLayout(contentPane,     // 将内容面板的布局设为 BoxLayout
                                            BoxLayout.Y_AXIS)); // 指定排列方向为 Y_AXIS（垂直排列）

        addAButton("Button 1", contentPane);                // 添加按钮 "Button 1"（垂直排列第1个）
        addAButton("2", contentPane);                       // 添加按钮 "2"（垂直排列第2个）
        addAButton("Button 3", contentPane);                // 添加按钮 "Button 3"（垂直排列第3个）
        addAButton("Long-Named Button 4", contentPane);     // 添加长文本按钮（垂直排列第4个）
        addAButton("Button 5", contentPane);                // 添加按钮 "Button 5"（垂直排列第5个）

        addWindowListener(new WindowAdapter() {             // 注册窗口事件监听器（使用匿名内部类继承 WindowAdapter）
            public void windowClosing(WindowEvent e) {      // 重写 windowClosing 方法：点击关闭按钮时触发
                System.exit(0);                             // 退出 Java 虚拟机，结束程序

            }                                               // windowClosing 方法结束
        });                                                 // 匿名内部类结束
    }                                                       // 构造方法结束

    // 辅助方法：创建按钮并设置对齐方式，然后添加到容器中
    private void addAButton(String text, Container container) { // 接收文字标签和容器对象
        JButton button = new JButton(text);                 // 创建带指定文字的按钮
        button.setAlignmentX(Component.CENTER_ALIGNMENT);   // 设置按钮在水平方向上居中对齐
        container.add(button);                              // 将按钮添加到容器中
    }                                                       // addAButton 方法结束

    public static void main(String args[]) {                // 主入口方法
        BoxWindow window = new BoxWindow();                 // 创建自定义窗口对象

        window.setTitle("BoxLayout");                       // 设置窗口标题
        window.pack();                                      // 自动调整窗口大小
        window.setVisible(true);                            // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束
