/**
 * 【功能说明】
 * 本文件演示了Java中内部类（Inner Class）的基本概念。
 * Outer（外部类）包含一个成员内部类Inner，Inner可以直接访问
 * 外部类的私有成员变量size。外部类通过调用内部类的方法来
 * 修改其成员变量。在main方法中，展示了外部类如何通过内部类
 * 间接完成操作。
 *
 * 【知识点】
 * 1. 成员内部类（Member Inner Class）：定义在另一个类内部的非静态类
 * 2. 内部类访问外部类成员：内部类可以直接访问外部类的所有成员
 *    （包括private成员），无需创建外部类对象引用
 * 3. 外部类访问内部类：外部类需要通过内部类的对象引用来访问内部类的成员
 * 4. 内部类的创建：在外部类中可以作为成员变量直接创建内部类对象
 * 5. 内部类的编译：内部类编译后会生成独立的.class文件（Outer$Inner.class）
 * 6. 内部类与外部类的关系：内部类持有对外部类对象的隐式引用
 */
package chp4_oo.exp4_11;                    // 声明包路径，该类属于chp4_oo.exp4_11包

/**
 * Outer类：外部类
 * 包含一个成员内部类Inner和一个私有成员变量size
 * 演示外部类如何使用内部类来操作其成员
 */
public class Outer {                         // 定义一个名为Outer的公共类

    private int size;                        // 私有成员变量size，外部类Outer的成员

    /**
     * Inner类：成员内部类
     * 定义在Outer类的内部，可以直接访问Outer类的所有成员（包括私有成员）
     * 内部类的doStuff方法直接操作外部类的成员变量size
     */
    public class Inner {                     // 内部类定义（成员内部类）
        /**
         * doStuff方法：内部类的方法
         * 直接访问和修改外部类的私有成员变量size
         * 内部类可以无条件访问外部类的所有成员（包括private修饰的成员）
         */
        public void doStuff() {              // 内部类的方法
            size++;                          // 直接访问外部类的私有成员变量size，将其自增1
        }                                    // 普通类外部无法访问Outer的private成员，但内部类可以
    }

    // 在外部类中声明一个成员变量i，类型为Inner，直接new创建Inner对象
    Inner i = new Inner();                   // 创建内部类Inner的实例作为外部类的成员变量

    /**
     * increaseSize方法：外部类的方法
     * 通过内部类对象i间接增加size的值
     * 外部类不能直接访问内部类的成员，必须通过内部类对象调用
     */
    public void increaseSize() {             // 外部类的方法
        i.doStuff();                         // 通过内部类对象i调用doStuff方法，间接操作size
    }                                        // 调用doStuff()后，size的值会增加1

    /**
     * main方法：Java程序入口点
     * 创建外部类对象，循环调用increaseSize方法，
     * 观察内部类如何通过外部类间接操作外部类的成员变量
     * @param a 命令行参数数组
     */
    public static void main(String[] a) {    // 主方法，JVM自动调用
        Outer o = new Outer();               // 创建外部类Outer的对象o
        // 注意：创建Outer对象时，其成员变量Inner i也会被一起创建

        for (int i = 0; i < 4; i++) {        // for循环，循环4次（i从0到3）
            o.increaseSize();                // 调用外部类对象o的increaseSize方法
            // 该方法内部调用i.doStuff()，使size自增1
            // 每调用一次increaseSize，size的值增加1

            // 输出当前size的值
            System.out.println("The value of size : " + o.size);
            // 第1次循环：size=1
            // 第2次循环：size=2
            // 第3次循环：size=3
            // 第4次循环：size=4
        }                                    // 循环结束，最终size的值为4
    }
}
