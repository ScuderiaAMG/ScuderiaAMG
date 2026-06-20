/**
 * 【功能说明】
 * 本程序演示了Java中包（package）和import语句的使用。
 * TestPackage类位于chp5_advanced.exp5_6包中，通过import语句
 * 引入了其他包中的Point和Rectangle类，创建对象并调用其方法。
 * 这展示了如何跨包使用自定义的类。
 *
 * 【知识点】
 * 1. package声明：类所在的包路径，与目录结构对应
 * 2. import语句：导入其他包中的类，使代码中可以使用类名（而非全限定名）
 * 3. 全限定名（Fully Qualified Name）：包含完整包路径的类名
 * 4. 类和包的组织：按功能模块组织在不同包中，形成层次化结构
 * 5. public类的跨包访问：只有声明为public的类才能被其他包访问
 * 6. 对象创建和消息传递（消息调用）：创建对象后调用其方法
 */
package chp5_advanced.exp5_6;                              // 声明主类所在的包路径

import chp5_advanced.exp5_6.graphics.twoD.Point;           // 导入Point类，使其可以在代码中直接使用短类名
import chp5_advanced.exp5_6.graphics.twoD.Rectangle;       // 导入Rectangle类，使其可以在代码中直接使用短类名

public class TestPackage {                                 // 主类（public），用于测试包的跨包使用
    public static void main(String args[]) {               // 主方法：程序执行的入口点
        Point p = new Point(2, 3);                         // 创建Point对象，坐标为(2,3)
        Rectangle r = new Rectangle(p, 10, 10);            // 创建Rectangle对象，以p为原点，宽和高均为10
        System.out.println("The area of the rectangle is " + r.area()); // 调用area()方法计算面积并输出结果
    }
}
