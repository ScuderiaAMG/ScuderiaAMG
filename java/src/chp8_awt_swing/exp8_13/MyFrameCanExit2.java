/**
 * 【功能说明】
 * 本程序演示使用内部类（Inner Class）作为窗口事件监听器。
 * 通过继承 WindowAdapter 并重写 windowClosing 方法，
 * 实现点击窗口关闭按钮时退出程序的功能。
 * 关键教学点是：将监听器定义为窗口类的内部类，
 * 通过"外部类实例.new 内部类构造方法"的方式创建监听器实例。
 *
 * 【知识点】
 * 1. 内部类作为监听器 —— WindowHandler 是 MyFrameCanExit2 的内部类，
 *    继承 WindowAdapter 并重写 windowClosing 方法。
 *    内部类可以访问外部类的私有成员（但本例中未体现这一优势）。
 * 2. addWindowListener() —— 为窗口注册 WindowListener 监听器，
 *    监听窗口的打开、关闭、激活、图标化等事件。
 * 3. WindowAdapter —— 窗口事件适配器，已经实现了 WindowListener 接口的所有7个方法（空实现），
 *    只需重写需要的方法即可，不必实现所有方法。
 * 4. 内部类实例化语法 —— fr.new WindowHandler()
 *    内部类实例必须依赖于一个外部类实例来创建。
 * 5. System.exit(0) —— 终止 JVM，参数0表示正常退出。
 */

package chp8_awt_swing.exp8_13;                             // 声明包路径，对应第8章AWT/Swing实验13

import java.awt.event.WindowAdapter;                        // 导入窗口事件适配器类
import java.awt.event.WindowEvent;                          // 导入窗口事件类

import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame

public class MyFrameCanExit2 extends JFrame {               // 继承 JFrame 创建自定义窗口类

    public static void main(String args[ ]) {               // 主入口方法
        MyFrameCanExit2 fr = new MyFrameCanExit2("Hello !");// 创建自定义窗口对象，标题为 "Hello !"
        fr.addWindowListener(fr.new WindowHandler());       // 注册窗口监听器：使用内部类实例（外部类实例.new 内部类构造）
        fr.setSize(200, 200);                               // 设置窗口宽200像素、高200像素
        fr.setVisible(true);                                // 使窗口可见
    }                                                       // main 方法结束

    public MyFrameCanExit2(String str) {                    // 构造方法，参数 str 为窗口标题
        super(str);                                         // 调用父类 JFrame 构造方法，设置标题
    }                                                       // 构造方法结束

    // 内部类：继承 WindowAdapter 作为窗口事件监听器
    class WindowHandler extends WindowAdapter {             // 定义内部类，继承窗口适配器
        public void windowClosing(WindowEvent e) {          // 重写 windowClosing：点击关闭按钮时触发
            System.exit(0);                                 // 退出 Java 虚拟机，结束程序
        }                                                   // windowClosing 方法结束
    }                                                       // 内部类 WindowHandler 结束

}                                                           // 类定义结束
