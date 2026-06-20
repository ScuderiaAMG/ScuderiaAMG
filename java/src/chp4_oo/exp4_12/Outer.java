/**
 * 【功能说明】
 * 本文件演示了Java中变量遮蔽（Variable Shadowing）的高级场景——
 * 当局部变量、内部类成员变量、外部类成员变量三者同名时的区分方法。
 * 在Inner内部类的doStuff方法中，参数size与内部类成员变量size、
 * 外部类成员变量size三者同名。通过以下方式区分：
 * - size：直接使用，访问的是局部变量（参数）
 * - this.size：访问的是内部类（Inner）的成员变量
 * - Outer.this.size：访问的是外部类（Outer）的成员变量
 *
 * 【知识点】
 * 1. 变量的作用域遮蔽：局部变量遮蔽内部类成员变量，内部类成员变量遮蔽外部类成员变量
 * 2. this关键字：在内部类中，this指向内部类自身的对象
 * 3. 外部类名.this：语法"外部类名.this"用于在内部类中引用外部类对象
 * 4. 内部类访问外部类成员：内部类可以访问外部类的所有成员（包括私有成员）
 * 5. 成员变量遮蔽的层次结构：局部变量 > 内部类成员变量 > 外部类成员变量
 * 6. System.out.println输出不同作用域的变量值，观察各自的变化
 */
package chp4_oo.exp4_12;                    // 声明包路径，该类属于chp4_oo.exp4_12包

/**
 * Outer类：外部类
 * 包含一个私有成员变量size和一个成员内部类Inner
 * 演示在内部类中如何区分同名的局部变量、内部类成员变量和外部类成员变量
 */
public class Outer {                         // 定义一个名为Outer的公共类

    private int size;                        // 外部类的私有成员变量size

    /**
     * Inner类：成员内部类
     * 也定义了一个名为size的成员变量（与外部类成员变量同名）
     * 内部类的doStuff方法有一个名为size的参数（与成员变量同名）
     * 这样就形成了三层同名的变量遮蔽结构
     */
    public class Inner {                     // 成员内部类定义

        private int size;                    // 内部类的私有成员变量size（与外部类的size同名）

        /**
         * doStuff方法：内部类的方法
         * 参数名为size，与内部类成员变量size和外部类成员变量size同名
         * 通过不同的语法形式区分三个不同作用域的size变量
         * @param size 局部变量（方法参数），与内部类和外部类的成员变量同名
         */
        public void doStuff(int size) {      // 方法，参数size是局部变量（与两个成员变量同名）
            size++;                          // 直接使用size：访问的是局部变量（方法参数），将参数值自增1
            this.size++;                     // this.size：访问的是内部类Inner的成员变量size，自增1
            Outer.this.size++;               // Outer.this.size：访问的是外部类Outer的成员变量size，自增1

            // 输出局部变量size的值（方法参数自增后的值）
            System.out.println("size in Inner.doStuff(): " + size);
            // 输出：size in Inner.doStuff(): <参数值+1>

            // 输出内部类成员变量size的值
            System.out.println("size of the Inner class: " + this.size);
            // 输出：size of the Inner class: <内部类成员变量值+1>

            // 输出外部类成员变量size的值
            System.out.println("size of the Outer class:  " + Outer.this.size);
            // 输出：size of the Outer class: <外部类成员变量值+1>
        }
    }

    // 创建内部类Inner的对象作为外部类的成员变量
    Inner i = new Inner();                   // 成员变量i，指向内部类Inner的实例

    /**
     * increaseSize方法：外部类的方法
     * 通过内部类对象i调用doStuff方法，传入一个size值
     * @param s 传入内部类doStuff方法的参数值
     */
    public void increaseSize(int s) {        // 外部类的方法，接收一个int参数s
        i.doStuff(s);                        // 调用内部类对象的doStuff方法，将s作为参数传入
    }

    /**
     * main方法：Java程序入口点
     * 创建外部类对象，调用increaseSize方法，观察三个不同作用域中size的变化
     * @param a 命令行参数数组
     */
    public static void main(String[] a) {    // 主方法，JVM自动调用
        Outer o = new Outer();               // 创建外部类Outer的对象实例o
        // 创建o时同时会创建内部类对象i（成员变量），此时：
        //   - Outer的size = 0（int默认值）
        //   - Inner的size = 0（int默认值）

        o.increaseSize(10);                  // 调用increaseSize方法，传入参数值10
        // 方法内部：i.doStuff(10)
        // doStuff方法执行：
        //   1. size++          -> 局部变量size从10变为11
        //   2. this.size++     -> 内部类成员变量size从0变为1
        //   3. Outer.this.size++ -> 外部类成员变量size从0变为1

        // 控制台输出：
        //   size in Inner.doStuff(): 11
        //   size of the Inner class: 1
        //   size of the Outer class:  1
    }
}
