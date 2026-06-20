/**
 * 【功能说明】
 * 本程序演示 Java 2D 图形绘制 API 的基本使用。
 * 通过继承 JPanel 并重写 paint(Graphics) 方法，在面板上绘制图形：
 *   1. 绘制一个橙色的背景面板
 *   2. 绘制一个青色的 3D 圆角矩形
 *   3. 绘制一个红色的椭圆
 * 展示了在 Swing 组件上进行自定义绘图的基本步骤和常用方法。
 *
 * 【知识点】
 * 1. paint(Graphics g) —— Swing 组件的绘制方法，当组件需要重绘时被自动调用。
 *    Graphics 对象提供了各种绘制图形的方法。
 * 2. setBackground(Color.ORANGE) —— 设置组件的背景色，在调用 super.paint(g) 时生效。
 * 3. super.paint(g) —— 调用父类 JPanel 的 paint 方法，完成默认绘制（如背景填充、边框等）。
 *    自定义绘制应该在 super.paint(g) 调用之后进行。
 * 4. Graphics 类的常用绘图方法：
 *    - setColor(Color) —— 设置当前绘图颜色
 *    - fill3DRect(x, y, width, height, raised) —— 绘制3D效果的填充矩形
 *      （raised=true 凸起，raised=false 凹陷）
 *    - drawOval(x, y, width, height) —— 绘制椭圆轮廓（宽度=高度时为正圆）
 *    更多方法：drawLine、drawRect、fillRect、drawRoundRect、fillOval、drawArc、fillArc 等。
 * 5. Color 颜色常量 —— Color.ORANGE、Color.cyan、Color.red 等预定义颜色。
 * 6. 坐标系统 —— Swing 组件的坐标原点 (0,0) 在组件的左上角，x 向右递增，y 向下递增。
 *    单位是像素。
 * 7. JPanel 作为画布 —— 将自定义绘图代码封装在 JPanel 的子类中，
 *    通过重写 paint 方法实现自定义绘制，再将面板添加到 JFrame 中。
 */

package chp8_awt_swing.exp8_18;                             // 声明包路径，对应第8章AWT/Swing实验18

import java.awt.Color;                                      // 导入颜色类，用于设置画笔和背景颜色
import java.awt.Graphics;                                   // 导入图形上下文类，提供各种绘图方法

import javax.swing.JFrame;                                  // 导入 Swing 顶层窗口类 JFrame
import javax.swing.JPanel;                                  // 导入 Swing 面板类 JPanel

// 自定义面板类：继承 JPanel，重写 paint 方法实现绘图
class MyPanel extends JPanel {                              // 定义包级私有面板类

    public void paint(Graphics g) {                         // 重写 paint 方法，参数 g 为图形上下文对象
        setBackground(Color.ORANGE);                        // 设置面板背景色为橙色
        super.paint(g);                                     // 调用父类 paint 方法，完成默认绘制（包括填充背景色）

        g.setColor(Color.cyan);                             // 将画笔颜色设为青色（青色 = 蓝绿色）
        g.fill3DRect(50, 50, 200, 90, false);               // 绘制3D填充矩形：左上角坐标(50,50)，宽200，高90，raised=false（凹陷效果）

        g.setColor(Color.red);                              // 将画笔颜色设为红色
        g.drawOval(300, 300, 100, 50);                      // 绘制椭圆轮廓：左上角坐标(300,300)，宽100，高50（非正圆）
    }                                                       // paint 方法结束

}                                                           // MyPanel 类定义结束

// 主类：包含程序入口方法
public class Demo8_18 {                                     // 定义公开类 Demo8_18

    public static void main(String[] args) {                // 主入口方法
        JFrame jf = new JFrame("我是画框");                  // 创建 JFrame 窗口对象，标题为"我是画框"
        jf.add(new MyPanel());                              // 创建自定义绘图面板并添加到窗口中
        jf.setSize(500, 500);                               // 设置窗口宽500像素、高500像素
        jf.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);  // 设定关闭窗口时退出程序
        jf.setVisible(true);                                // 使窗口可见
    }                                                       // main 方法结束

}                                                           // 类定义结束
