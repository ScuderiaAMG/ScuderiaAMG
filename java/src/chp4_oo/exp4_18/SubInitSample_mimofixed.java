/**
 * 【功能说明】
 * 本文件演示了Java中继承关系下的类加载和对象初始化顺序。
 * 包含三个类：A（父类）、B（继承A的子类）、C（一个辅助类，用于跟踪初始化时机）。
 * 通过在不同初始化阶段（静态变量、静态块、实例块、构造方法）创建C类对象，
 * 可以清晰观察Java在继承体系中的完整初始化流程。
 * 运行main方法将展示：父类静态成员 -> 子类静态成员 -> 父类实例成员
 * -> 父类构造方法 -> 子类实例成员 -> 子类构造方法的执行顺序。
 *
 * 【知识点】
 * 1. 继承体系下的初始化顺序：父类静态 -> 子类静态 -> 父类非静态 -> 子类非静态
 * 2. 静态变量在类加载时被初始化，且仅初始化一次
 * 3. 静态初始化块在类加载时按照代码顺序执行
 * 4. 实例初始化块在每次创建对象时执行，且在构造方法之前
 * 5. 用private static修饰的内部类可以实现信息隐藏
 * 6. 即使子类构造方法中没有显式写super()，也会默认调用父类的无参构造方法
 */
package chp4_oo.exp4_18;  // 包声明，表明当前类位于chp4_oo.exp4_18包中

/**
 * SubInitSample类——测试类，包含main方法作为程序入口
 * 用于演示继承体系下的初始化顺序
 */
public class SubInitSample_mimofixed {
    /**
     * 主方法，程序的入口
     * @param args 命令行参数数组
     */
    public static void main(String[] args) {
        new B();  // 创建B类（子类）的实例，触发类加载和对象初始化过程
    }

    /**
     * A类——父类，用private static修饰，是SubInitSample的私有静态内部类
     * 私有静态内部类只能在SubInitSample内部被访问
     */
    private static class A {
        // 静态变量c，在类加载时创建C类实例并赋值
        public static C c = new C("A");
        // 静态初始化块，在类加载时执行
        static {
            System.out.println("A类static块");
        }
        // 实例初始化块（普通块），在每次创建对象时执行（在构造方法之前）
        {
            System.out.println("A类普通块");
        }
        // 无参构造方法
        public A() {
            System.out.println("A的构造方法");
        }
    }

    /**
     * B类——子类，继承自A，用private static修饰，是SubInitSample的私有静态内部类
     * 私有静态内部类只能在SubInitSample内部被访问
     */
    private static class B extends A {
        // 静态变量c，在类加载时创建C类实例并赋值
        public static C c = new C("B");
        // 静态初始化块，在类加载时执行
        static {
            System.out.println("B类static块");
        }
        // 实例初始化块（普通块），在每次创建对象时执行（在构造方法之前）
        {
            System.out.println("B类普通块");
        }
        // 无参构造方法，默认会调用父类A的无参构造方法super()
        public B() {
            System.out.println("B的构造方法");
        }
    }

    /**
     * C类——辅助类，用于跟踪初始化时机
     * 当C类的构造方法被调用时，会打印出调用者的标识id
     * 从而帮助跟踪初始化顺序
     */
    private static class C {
        String id;  // C类对象的标识字符串，用于区分是哪个类触发的初始化

        /**
         * C类的有参构造方法
         * @param id 标识字符串，用于在输出时区分调用来源
         */
        public C(String id) {
            this.id = id;  // 保存标识字符串
            System.out.println(this.id + "调用C的构造方法 ");  // 打印调用来源信息
        }
    }
}
