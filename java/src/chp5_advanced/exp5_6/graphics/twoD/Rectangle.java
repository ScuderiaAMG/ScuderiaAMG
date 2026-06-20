/**
 * 【功能说明】
 * 本文件定义了Rectangle（矩形）类，是二维图形库的组成部分。
 * 矩形由原点（origin，即左上角坐标点）、宽度（width）和高度（height）确定。
 * 提供了构造方法、移动矩形（move）和计算面积（area）的功能。
 *
 * 【知识点】
 * 1. 类的组合（Composition）：一个类将其他类的对象作为成员变量（如Rectangle包含Point对象origin）
 * 2. 构造方法重载（Overloaded Constructor）：类可以有多个不同参数列表的构造方法（此处部分被注释）
 * 3. this()调用：在一个构造方法中使用this(...)调用同一类的另一个构造方法（代码中被注释）
 * 4. 方法定义：定义类的行为，如move()和area()
 * 5. 包级别访问控制：public类可以被其他包访问
 * 6. 通过对象引用修改成员变量：move()方法直接修改origin对象的x、y值
 */
package chp5_advanced.exp5_6.graphics.twoD;               // 声明包路径，该文件位于chp5_advanced.exp5_6.graphics.twoD包中

public class Rectangle {                                   // 公有的Rectangle类，表示二维平面中的矩形
    public int width = 0;                                  // 公有的实例变量width（宽度），初始值为0
    public int height = 0;                                 // 公有的实例变量height（高度），初始值为0
    public Point origin;                                   // 公有的实例变量origin（原点/左上角坐标），类型为Point

    // 以下是被注释掉的三个构造方法，展示了构造方法重载的多种形式
    /*   public Rectangle() {                              // 无参构造方法（已注释）
            origin = new Point(0, 0);                      // 创建一个原点为(0,0)的Point对象赋给origin（已注释）
        }
        public Rectangle(Point p) {                        // 接收一个Point参数的构造方法（已注释）
            origin = p;                                    // 将参数Point对象赋给origin（已注释）
        }
        public Rectangle(int w, int h) {                   // 接收宽度和高度的构造方法（已注释）
            this(new Point(0, 0), w, h);                   // 通过this()调用另一个构造方法，创建原点为(0,0)的矩形（已注释）
        }*/

    public Rectangle(Point p, int w, int h) {              // 接收原点、宽度和高度的构造方法（当前唯一启用的构造方法）
        origin = p;                                        // 将参数中的Point对象赋值给成员变量origin
        width = w;                                         // 将参数中的宽度值赋值给成员变量width
        height = h;                                        // 将参数中的高度值赋值给成员变量height
    }

    // 移动矩形的方法
    public void move(int x, int y) {                       // move方法：将矩形移动至新的坐标位置
        origin.x = x;                                      // 修改origin对象的x坐标为参数x的值
        origin.y = y;                                      // 修改origin对象的y坐标为参数y的值
    }

    // 计算矩形面积的方法
    public int area() {                                    // area方法：计算并返回矩形的面积
        return width * height;                             // 返回宽度乘以高度得到的面积值
    }
}
