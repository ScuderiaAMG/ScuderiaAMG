/**
 * 【功能说明】
 * 本程序演示了Java面向对象编程中的多态性（Polymorphism）
 * 和接口（interface）的使用。定义了一个Shape接口以及三个实现类
 * （Circle、Square、Triangle），通过接口类型的数组和统一的draw()方法调用，
 * 展示了"一个接口，多种实现"的多态特性。程序使用Random随机生成图形对象，
 * 并统一调用其draw()方法。
 *
 * 【知识点】
 * 1. interface（接口）：完全抽象的类，只包含方法声明（JDK8前），实现类必须实现所有接口方法
 * 2. 多态（Polymorphism）：父类型引用指向子类型对象，调用同一方法表现出不同行为
 * 3. 接口类型的数组：可以存放任意实现了该接口的类的对象
 * 4. Random类：java.util包中用于生成随机数的工具类
 * 5. switch语句：根据随机数结果选择创建不同的图形对象
 * 6. 面向接口编程（Interface-Oriented Design）：提高代码的可扩展性和可维护性
 * 7. 动态绑定（Dynamic Binding）：运行时根据实际对象类型确定调用哪个方法
 */
package chp5_advanced.exp5_5;                              // 声明包路径，该文件位于chp5_advanced.exp5_5包中

import java.util.*;                                        // 导入java.util包下的所有类（用于使用Random类）

// 定义Shape接口
interface Shape {                                          // 接口Shape：声明所有图形类必须实现的方法
    void draw();                                           // 抽象方法draw()：绘制图形（无方法体，由实现类提供具体实现）
    void erase();                                          // 抽象方法erase()：擦除图形（无方法体，由实现类提供具体实现）
}

// 定义Circle类，实现Shape接口
class Circle implements Shape {                            // Circle（圆形）类实现Shape接口
    public void draw() {                                   // 实现接口中的draw()方法
        System.out.println("Calling Circle.draw()");       // 输出"调用Circle.draw()"
    }

    public void erase() {                                  // 实现接口中的erase()方法
        System.out.println("Calling Circle.erase()");      // 输出"调用Circle.erase()"
    }
}

// 定义Square类，实现Shape接口
class Square implements Shape {                            // Square（正方形）类实现Shape接口
    public void draw() {                                   // 实现接口中的draw()方法
        System.out.println("Calling Square.draw()");       // 输出"调用Square.draw()"
    }

    public void erase() {                                  // 实现接口中的erase()方法
        System.out.println("Calling Square.erase()");      // 输出"调用Square.erase()"
    }
}

// 定义Triangle类，实现Shape接口
class Triangle implements Shape {                          // Triangle（三角形）类实现Shape接口
    public void draw() {                                   // 实现接口中的draw()方法
        System.out.println("Calling Triangle.draw()");     // 输出"调用Triangle.draw()"
    }

    public void erase() {                                  // 实现接口中的erase()方法
        System.out.println("Calling Triangle.erase()");    // 输出"调用Triangle.erase()"
    }
}

// 定义包含main()方法的主类
public class NewShapes {                                   // 主类（public），包含程序入口main方法和图形操作静态方法

    static void drawOneShape(Shape s) {                    // 静态方法：绘制单个图形，参数为Shape接口类型
        s.draw();                                          // 调用传入对象的draw()方法（多态：实际调用的是具体实现类的draw()）
    }

    static void drawShapes(Shape[] ss) {                   // 静态方法：遍历图形数组并逐一绘制
        for (int i = 0; i < ss.length; i++) {              // 使用for循环遍历Shape数组中的所有元素
            ss[i].draw();                                  // 调用每个图形对象的draw()方法（多态动态绑定）
        }
    }

    public static void main(String[] args) {               // 主方法：程序执行的入口点
        Random rand = new Random();                        // 创建Random对象，用于生成随机数
        Shape[] s = new Shape[9];                          // 创建Shape接口类型的数组，长度为9，可以存放任何实现了Shape的类的对象

        for (int i = 0; i < s.length; i++) {               // 使用for循环遍历数组，为每个元素随机创建一种图形对象
            switch (rand.nextInt(3)) {                     // 生成0~2之间的随机整数，用于决定创建哪种图形
                case 0:                                    // 如果随机数为0
                    s[i] = new Circle();                   // 创建Circle对象并赋值给数组元素
                    break;                                 // 跳出switch语句
                case 1:                                    // 如果随机数为1
                    s[i] = new Square();                   // 创建Square对象并赋值给数组元素
                    break;                                 // 跳出switch语句
                case 2:                                    // 如果随机数为2
                    s[i] = new Triangle();                 // 创建Triangle对象并赋值给数组元素
                    break;                                 // 跳出switch语句
            }
        }

        drawShapes(s);                                     // 调用drawShapes方法，传图形数组，统一绘制所有图形（多态调用）
    }
}
