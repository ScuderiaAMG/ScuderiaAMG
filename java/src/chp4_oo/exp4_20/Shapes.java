/**
 * 【功能说明】
 * 本文件演示了Java中的多态（Polymorphism）——面向对象编程的三大特性之一。
 * 定义了Shape基类和三个子类（Circle、Square、Triangle），每个子类都重写了
 * draw()和erase()方法。
 * Shapes类中的drawOneShape()方法接受Shape类型的参数，但实际传入子类对象时，
 * 会自动调用子类重写后的方法（动态绑定）。
 * drawShapes()方法接受Shape数组，遍历数组中的每个元素并调用draw()方法。
 * main方法创建包含9个随机形状的数组（使用Random随机生成），然后调用drawShapes()
 * 统一绘制所有形状。
 *
 * 【知识点】
 * 1. 多态（Polymorphism）—— 同一操作作用于不同对象，产生不同的执行结果
 * 2. 动态绑定（Dynamic Binding）—— JVM在运行时根据对象的实际类型调用对应的方法
 * 3. 向上转型（Upcasting）—— 子类对象可以赋值给父类类型的引用变量
 * 4. 继承（Inheritance）—— 子类通过extends关键字继承父类
 * 5. 方法重写（Method Overriding）—— 子类重写父类的方法
 * 6. Random类的使用——生成随机数
 * 7. switch语句的使用——根据随机值选择创建不同的子类对象
 */
package chp4_oo.exp4_20;  // 包声明，表明当前类位于chp4_oo.exp4_20包中

// 导入java.util包中的Random类，用于生成随机数
import java.util.Random;

/**
 * Shape类——抽象形状基类，定义了所有形状共有的操作接口
 * 此处使用了具体类而非抽象类
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
 * Shapes类——绘图测试类，包含main方法作为程序入口
 * 通过多态机制统一处理所有形状
 */
public class Shapes{
    /**
     * drawOneShape()方法——绘制单个形状
     * 参数类型为Shape（父类类型），但实际传入子类对象时体现多态性
     * @param s Shape类型的引用，可以指向任何Shape子类对象
     */
    static void drawOneShape(Shape s){
        s.draw();  // 动态绑定：根据s实际指向的对象类型调用对应的draw()方法
    }

    /**
     * drawShapes()方法——绘制形状数组中的所有形状
     * 使用循环遍历数组，对每个元素调用draw()方法
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
            // 使用switch语句根据随机值决定创建哪种形状
            switch(rand.nextInt(3)) {   // rand.nextInt(3)返回0、1、2中的随机一个数
                case 0: s[i] = new Circle();break;   // 随机数为0时创建Circle对象
                case 1: s[i] = new Square();break;   // 随机数为1时创建Square对象
                case 2: s[i] = new Triangle();break; // 随机数为2时创建Triangle对象
            }
        }
        drawShapes(s);  // 使用drawShapes()方法绘制数组中的所有形状
    }
}
