/**
 * 【功能说明】
 * 本程序演示使用匿名内部类（Anonymous Inner Class）作为窗口事件监听器。
 * 匿名内部类无需显式定义类名，直接在 addWindowListener 方法的参数中
 * 创建 WindowAdapter 的子类并重写 windowClosing 方法。
 * 这是 Swing 编程中最常见的窗口关闭事件处理方式，代码简洁高效。
 *
 * 【知识点】
 * 1. 匿名内部类 —— 没有名字的内部类，在创建对象的同时定义类的实现。
 *    语法：new 父类/接口() { 重写的方法 }
 *    优势：代码紧凑，适合只需使用一次的监听器。
 * 2. WindowAdapter —— 窗口事件适配器类，已提供所有方法的空实现。
 *    匿名内部类继承它，只需重写需要的方法（如 windowClosing），
 *    无需逐个实现 WindowListener 接口的7个方法。
 * 3. addWindowListener() —— JFrame 的方法，注册窗口事件监听器。
 * 4. System.exit(0) —— 终止 JVM，0 表示正常退出。
 * 5. 对比 exp8_13（内部类方式）和 exp8_14（匿名内部类方式）：
 *    - 内部类方式：需显式定义类名，通过 fr.new 创建实例，适合复用。
 *    - 匿名内部类方式：无类名，在参数位置直接创建，适合一次性使用。
 *    两种方式在功能上完全等价，匿名内部类代码更简洁。
 */

package chp8_awt_swing.exp8_14;                             // 声明包路径，对应第8章AWT/Swing实验14

import java.awt.event.WindowAdapter;                        // 导入窗口事件适配器类
import java.awt.event.WindowEvent;                          // 导入窗口事件类

import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame

public class MyFrameCanExit3 extends JFrame {               // 继承 JFrame 创建自定义窗口类

    public static void main(String args[ ]) {               // 主入口方法
        MyFrameCanExit3 fr = new MyFrameCanExit3("Hello !");// 创建自定义窗口对象，标题为 "Hello !"
        fr.addWindowListener( new WindowAdapter(){           // 注册窗口监听器（匿名内部类方式）
            public void windowClosing(WindowEvent e) {       // 重写 windowClosing 方法：点击关闭按钮时触发
                System.exit(0);                              // 退出 Java 虚拟机，结束程序
            }                                                // windowClosing 方法结束
        });                                                  // 匿名内部类及 addWindowListener 调用结束
        fr.setSize(200, 200);                                // 设置窗口宽200像素、高200像素
        fr.setVisible(true);                                 // 使窗口可见
    }                                                        // main 方法结束

    public MyFrameCanExit3(String str) {                     // 构造方法，参数 str 为窗口标题
        super(str);                                          // 调用父类 JFrame 构造方法，设置标题
    }                                                        // 构造方法结束

}                                                            // 类定义结束
