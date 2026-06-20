/**
 * 【功能说明】
 * 本文件演示了Java中父类与子类的完整初始化顺序。
 * Parent类（父类）和SubClass类（子类）都包含：
 *   1. 静态变量声明
 *   2. 实例变量声明
 *   3. 静态初始化块
 *   4. 实例初始化块（普通块）
 *   5. 构造方法
 * 通过运行main方法，可以清晰观察到类加载和对象创建时各部分的执行顺序。
 *
 * 【知识点】
 * 1. Java类的完整初始化顺序：
 *    a. 加载父类，执行父类的静态变量和静态初始化块（按声明顺序）
 *    b. 加载子类，执行子类的静态变量和静态初始化块（按声明顺序）
 *    c. 执行父类的实例变量初始化和实例初始化块（按声明顺序）
 *    d. 执行父类的构造方法
 *    e. 执行子类的实例变量初始化和实例初始化块（按声明顺序）
 *    f. 执行子类的构造方法
 * 2. 静态成员属于类级别，在类加载时初始化，仅一次
 * 3. 实例成员属于对象级别，在每次创建对象时初始化
 * 4. 实例初始化块在构造方法之前执行
 * 5. 继承体系下，总是先执行父类的初始化，再执行子类的初始化
 */
package chp4_oo.exp4_18;  // 包声明，表明当前类位于chp4_oo.exp4_18包中

/**
 * Parent类——父类，展示父类中各成员的初始化顺序
 */
class Parent {
    // 父类静态变量（类变量）
    public static String p_StaticField = "父类--静态变量";  // 静态变量，类加载时初始化

    // 父类实例变量
    public String p_Field = "父类--变量";  // 实例变量，创建对象时初始化
    protected int i = 9;   // 受保护的整型成员变量，初始值为9
    protected int j = 0;   // 受保护的整型成员变量，初始值为0

    // 父类静态初始化块，在类加载时执行
    static {
        System.out.println(p_StaticField);  // 先打印静态变量的值："父类--静态变量"
        System.out.println("父类--静态初始化块");  // 再打印静态初始化块标识
    }

    // 父类实例初始化块（普通块），在每次创建对象时执行（在构造方法之前）
    {
        System.out.println(p_Field);       // 先打印实例变量的值："父类--变量"
        System.out.println("父类--初始化块");  // 再打印实例初始化块标识
    }

    // 父类构造方法
    public Parent() {
        System.out.println("父类--构造器");   // 打印构造器标识
        System.out.println("i=" + i + ", j=" + j);  // 打印当前i和j的值（i=9, j=0）
        j = 20;  // 将j的值修改为20
    }
}

/**
 * SubClass类——子类，继承自Parent类，展示子类中各成员的初始化顺序
 */
public class SubClass extends Parent {
    // 子类静态变量（类变量）
    public static String s_StaticField = "子类--静态变量";  // 静态变量，类加载时初始化

    // 子类实例变量
    public String s_Field = "子类--变量";  // 实例变量，创建对象时初始化

    // 子类静态初始化块，在子类类加载时执行
    static {
        System.out.println(s_StaticField);  // 先打印静态变量的值："子类--静态变量"
        System.out.println("子类--静态初始化块");  // 再打印静态初始化块标识
    }

    // 子类实例初始化块（普通块），在每次创建对象时执行（在构造方法之前）
    {
        System.out.println(s_Field);       // 先打印实例变量的值："子类--变量"
        System.out.println("子类--初始化块");  // 再打印实例初始化块标识
    }

    // 子类构造方法
    public SubClass() {
        System.out.println("子类--构造器");   // 打印构造器标识
        System.out.println("i=" + i + ",j=" + j);  // 打印继承自父类的i和j的值
        // 父类构造方法中已将j改为20，所以此处j=20
    }

    // 程序入口main方法（在SubClass类中）
    public static void main(String[] args) {
        System.out.println("进入main方法");  // main方法开始执行的标识
        new SubClass();  // 创建SubClass实例，触发完整的初始化过程
    }
}
