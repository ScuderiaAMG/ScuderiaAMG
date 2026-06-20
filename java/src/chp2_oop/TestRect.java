/**
 * ============================================================
 * 【功能说明】
 * 矩形类的测试程序，用于演示如何创建 Rectangle 类的对象实例，
 * 并通过构造方法初始化对象的属性，然后调用对象的方法进行运算。
 * 本类包含了 main 方法，可以直接运行，分别计算两个不同尺寸矩形的
 * 周长和面积，并将结果输出到控制台。
 * 这是将类的定义（Rectangle.java）与类的使用（TestRect.java）分离的经典示例。
 * ============================================================
 * 【知识点】
 * 1. 类的分离定义与使用 —— 将类的定义放在一个文件中，使用放在另一个文件中。
 * 2. 跨文件类调用 —— 在同一个包内，一个类可以直接使用另一个包级私有的类。
 * 3. new + 构造方法 —— 创建对象的标准方式，同时传入初始化参数。
 * 4. 对象引用变量 —— 声明类型为类名的变量，保存对象的引用（内存地址）。
 * 5. 方法调用 —— 通过"对象名.方法名()"的方式调用对象的实例方法。
 * 6. 封装访问 —— 通过构造方法间接初始化 private 字段（而非直接赋值）。
 * 7. 编译单元规范 —— 一个 .java 文件可以包含多个类，但只能有一个 public 类。
 * ============================================================
 */

// 声明包名为 chp2_oop，与 Rectangle.java 位于同一个包中
// 同一包内的类可以互相访问（即使没有 public 修饰符也能访问）
package chp2_oop;

// 定义一个名为 TestRect 的公共测试类
// public: 该类是公共类，可以被其他包访问
// 因为这是一个测试类，通常需要被更广泛的访问
// 注意：由于有 public 关键字，文件名必须与类名一致（TestRect.java）
public class TestRect {

    // main 方法：程序的入口点
    // public static void: 标准的 main 方法签名
    // String[] args: 接收命令行传入的参数
    public static void main(String[] args) {

        // 创建 Rectangle 类的第一个对象 rect1
        // Rectangle rect1: 声明一个 Rectangle 类型的引用变量
        // new Rectangle(10, 5): 调用 Rectangle 类的有参构造方法
        //   传入实参 10 作为长度（l），5 作为宽度（w）
        //   Java 会在堆内存中为新对象分配空间
        //   构造方法内部执行 this.l = 10; this.w = 5; 完成初始化
        //   返回对象的引用（内存地址），赋值给变量 rect1
        Rectangle rect1 = new Rectangle(10, 5);

        // 创建 Rectangle 类的第二个对象 rect2
        // new Rectangle(6, 4): 调用构造方法传入不同的参数值
        //   rect2 的长度 l = 6，宽度 w = 4
        // rect1 和 rect2 是内存中两个完全独立的对象
        Rectangle rect2 = new Rectangle(6, 4);

        // 调用 rect1 对象的 perimeter() 方法计算周长
        // rect1.perimeter(): 通过"对象名.方法名()"调用实例方法
        // 方法内部使用 rect1 的 l 和 w 字段计算：2 * (10 + 5) = 30
        // 使用字符串连接运算符 + 拼接输出内容
        // 输出结果: perimeter of rect1 = 30
        System.out.println("perimeter of rect1 = " + rect1.perimeter());

        // 调用 rect1 对象的 area() 方法计算面积
        // rect1.area(): 使用 rect1 的 l 和 w 计算：10 * 5 = 50
        // 输出结果: area of rect1 = 50
        System.out.println("area of rect1 = " + rect1.area());

        // 调用 rect2 对象的 perimeter() 方法计算周长
        // rect2.perimeter(): 使用 rect2 的 l 和 w 计算：2 * (6 + 4) = 20
        // 输出结果: perimeter of rect2 = 20
        System.out.println("perimeter of rect2 = " + rect2.perimeter());

        // 调用 rect2 对象的 area() 方法计算面积
        // rect2.area(): 使用 rect2 的 l 和 w 计算：6 * 4 = 24
        // 输出结果: area of rect2 = 24
        System.out.println("area of rect2 = " + rect2.area());

    // 右花括号表示 main 方法的结束
    }

// 右花括号表示 TestRect 类的结束
}
