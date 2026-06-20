/**
 * 【功能说明】
 * 本文件演示了Java中的成员内部类（Member Inner Class）。
 * Outer类中定义了一个名为Inner的内部类，该内部类可以访问外部类的私有成员变量size。
 * TestInner类作为测试入口，演示了如何通过外部类对象创建内部类对象的语法：
 *     Outer.Inner in = out.new Inner();
 * 内部类对象持有对外部类对象的隐式引用，因此可以直接访问外部类的成员。
 *
 * 【知识点】
 * 1. 成员内部类（Member Inner Class）—— 定义在外部类内部、方法外部的类
 * 2. 内部类可以无条件访问外部类的所有成员（包括private成员）
 * 3. 创建内部类对象必须依赖于外部类对象：outer.new Inner()
 * 4. 内部类的类型名使用"外部类名.内部类名"的格式（如Outer.Inner）
 * 5. 内部类对象会隐式持有外部类对象的引用（Outer.this）
 */
package chp4_oo.exp4_14;  // 包声明，表明当前类位于chp4_oo.exp4_14包中

/**
 * Outer类——外部类，包含一个成员内部类Inner
 */
class Outer{
    // 外部类的私有成员变量size，默认初始化为0
    private int size;

    /**
     * Inner类——成员内部类，定义在Outer类内部
     * 内部类可以自由访问外部类的所有成员
     */
    class Inner{
        /**
         * doStuff()方法——演示内部类访问外部类成员
         * 内部类可以直接访问外部类的私有变量size
         */
        void doStuff(){
            size++;  // 直接访问并修改外部类的私有成员变量size
            System.out.println("The size value of the Outer class: "+size);
        }
    }
}

/**
 * TestInner类——测试类，包含main方法作为程序入口
 * 演示如何创建和使用成员内部类
 */
public class TestInner{
    /**
     * 主方法，程序的入口
     * @param a 命令行参数数组
     */
    public static void main(String[] a){
        Outer out=new Outer();          // 首先创建外部类Outer的实例
        Outer.Inner in=out.new Inner(); // 通过外部类对象创建内部类对象的语法：outerObj.new Inner()
        // 类型为Outer.Inner，表示内部类的完整限定类型名

        in.doStuff();  // 调用内部类的方法，该方法会访问并修改外部类的成员变量
    }
}
