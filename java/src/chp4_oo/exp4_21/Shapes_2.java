/**
 * 【功能说明】
 * 本文件是"多态"的进阶演示，在Shapes.java的基础上新增了Pentagon（五边形）类，
 * 以展示多态机制的"可扩展性"（Extensibility）。
 * 当系统需要增加新的形状时，只需新增一个继承自Shape的子类并重写draw()和erase()
 * 方法即可，已有的drawShapes()等代码无需任何修改。
 * main方法中switch的随机范围从3改为4（rand.nextInt(4)），新增case 3用于创建
 * Pentagon对象，演示了在遵循开闭原则（Open-Closed Principle）的前提下扩展功能。
 *
 * 【知识点】
 * 1. 多态的可扩展性（Extensibility）—— 新增子类时无需修改已有代码
 * 2. 开闭原则（Open-Closed Principle）—— 对扩展开放，对修改关闭
 * 3. 动态绑定的优势—— 通过父类引用调用方法时自动选择实际子类的版本
 * 4. 向上转型的安全性—— 子类对象可以安全地赋值给父类引用
 * 5. 数组长度属性.length—— 用于遍历数组
 * 6. switch语句的扩展—— 增加case分支以支持新的子类
 * 7. 面向接口/父类编程（Programming to an Interface/Supertype）
 */
package chp4_oo.exp4_21;  // 包声明，表明当前类位于chp4_oo.exp4_21包中

// 导入java.util包中的Random类，用于生成随机数
import java.util.Random;

/**
 * Shape类——抽象形状基类，定义了所有形状共有的操作接口
 * 是面向对象多态机制的基础
 */
class Shape {
    // draw()方法——绘制形状（基类中为空实现，由子类具体实现）
    void draw() {}
    // erase()方法——擦除形状（基类中为空实现，由子类具体实现）
    void erase() {}
}

/**
 * Circle类——圆形类，继承自Shape类，实现了圆形特有的绘制和擦除方法
 */
class Circle extends Shape {
    // 重写父类的draw()方法，实现圆形的绘制
    void draw() {
        System.out.println("Calling Circle.draw()");  // 输出"Calling Circle.draw()"
    }
    // 重写父类的erase()方法，实现圆形的擦除
    void erase() {
        System.out.println("Calling Circle.erase()");  // 输出"Calling Circle.erase()"
    }
}

/**
 * Square类——方形类，继承自Shape类，实现了方形特有的绘制和擦除方法
 */
class Square extends Shape {
    // 重写父类的draw()方法，实现方形的绘制
    void draw() {
        System.out.println("Calling Square.draw()");  // 输出"Calling Square.draw()"
    }
    // 重写父类的erase()方法，实现方形的擦除
    void erase() {
        System.out.println("Calling Square.erase()");  // 输出"Calling Square.erase()"
    }
}

/**
 * Triangle类——三角形类，继承自Shape类，实现了三角形特有的绘制和擦除方法
 */
class Triangle extends Shape {
    // 重写父类的draw()方法，实现三角形的绘制
    void draw() {
        System.out.println("Calling Triangle.draw()");  // 输出"Calling Triangle.draw()"
    }
    // 重写父类的erase()方法，实现三角形的擦除
    void erase() {
        System.out.println("Calling Triangle.erase()");  // 输出"Calling Triangle.erase()"
    }
}

/**
 * Pentagon类——五边形类，继承自Shape类，是本次新增的形状类
 * 展示了在不修改已有代码的情况下扩展系统功能（开闭原则）
 */
class Pentagon extends Shape{
    // 重写父类的draw()方法，实现五边形的绘制
    void draw() {
        System.out.println("Calling Pentagon.draw()");  // 输出"Calling Pentagon.draw()"
    }
    // 重写父类的erase()方法，实现五边形的擦除
    void erase() {
        System.out.println("Calling Pentagon.erase()");  // 输出"Calling Pentagon.erase()"
    }
}

/**
 * Shapes_2类——绘图测试类（版本2），包含main方法作为程序入口
 * 在Shapes.java的基础上新增了Pentagon形状的支持
 */
public class Shapes_2 {
    /**
     * drawOneShape()方法——绘制单个形状（完全复用，无需修改）
     * 参数类型为Shape（父类类型），利用多态性统一处理所有形状
     * @param s Shape类型的引用，可以指向任何Shape子类对象
     */
    static void drawOneShape(Shape s){
        s.draw();  // 动态绑定：根据s实际指向的对象类型调用对应的draw()方法
    }

    /**
     * drawShapes()方法——绘制形状数组中的所有形状（完全复用，无需修改）
     * 即使新增了Pentagon类，此方法也不需要做任何改动
     * @param ss Shape类型的数组，可以存储任何Shape子类对象
     */
    static void drawShapes(Shape[] ss){
        // 使用for循环遍历整个形状数组
        for(int i = 0; i < ss.length; i++){
            ss[i].draw();  // 动态绑定：根据每个元素的实际类型调用对应的draw()方法
        }
    }

    /**
     * 主方法，程序的入口
     * @param args 命令行参数数组
     */
    public static void main(String[] args) {
        Random rand = new Random();     // 创建Random对象，用于生成随机数
        Shape[] s = new Shape[9];       // 创建长度为9的Shape类型数组（存储各种形状）

        // 使用for循环填充数组中的每个元素
        for(int i = 0; i < s.length; i++){
            // rand.nextInt(4)返回0、1、2、3中的随机一个数（相比Shapes.java扩展了范围）
            switch(rand.nextInt(4)) {
                case 0: s[i] = new Circle();break;   // 随机数为0时创建Circle对象
                case 1: s[i] = new Square();break;   // 随机数为1时创建Square对象
                case 2: s[i] = new Triangle();break; // 随机数为2时创建Triangle对象
                case 3: s[i] = new Pentagon();break; // 随机数为3时创建Pentagon对象（新增）
            }
        }
        drawShapes(s);  // 使用drawShapes()方法绘制数组中的所有形状
    }
}
