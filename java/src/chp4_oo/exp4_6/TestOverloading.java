/**
 * 【功能说明】
 * 本文件演示了Java中方法重载（Overloading）的概念，具体展示了
 * System.out.println()方法的重载。println方法有多种重载版本，
 * 可以接受boolean、char、int、long、float、double、char[]、String、
 * Object等不同类型的参数，并根据参数类型选择对应的重载版本进行输出。
 *
 * 【知识点】
 * 1. 方法重载（Overloading）：在同一个类中，多个方法可以有相同的方法名，
 *    但参数列表必须不同（参数类型、个数或顺序不同）
 * 2. println方法的重载：PrintStream类中定义了多个println重载版本，
 *    分别对应不同的数据类型
 * 3. 编译时多态：方法重载是编译时多态，编译器根据参数类型在编译阶段
 *    确定调用哪个重载版本
 * 4. 默认构造方法：当类中没有显式定义构造方法时，编译器会自动生成一个
 *    无参的默认构造方法
 * 5. char[]数组的特殊性：println(char[])会输出字符数组的内容，而不是地址
 * 6. toString方法：println(Object)会调用对象的toString方法，
 *    将对象转换为字符串后输出
 */
package chp4_oo.exp4_6;                     // 声明包路径，该类属于chp4_oo.exp4_6包

/**
 * TestOverloading类：方法重载测试类
 * 演示System.out.println方法根据不同类型参数的重载特性
 */
public class TestOverloading {               // 定义一个名为TestOverloading的公共类

    /**
     * main方法：Java程序入口点
     * 创建各种不同类型的变量，分别通过println方法输出
     * 观察println方法如何根据参数类型选择对应的重载版本
     * @param args 命令行参数数组
     */
    public static void main(String[] args) { // 主方法，JVM自动调用
        boolean b = true;                    // 声明boolean类型变量b并赋值为true
        char c = 'A';                        // 声明char类型变量c并赋值为字符'A'
        int i = 100;                         // 声明int类型变量i并赋值为100
        long l = 1000;                       // 声明long类型变量l并赋值为1000L
        float f = 99.0f;                     // 声明float类型变量f并赋值为99.0（加f后缀表示float）
        double d = 999.0;                    // 声明double类型变量d并赋值为999.0

        // 声明并初始化一个char类型数组，包含字符'A'、'B'、'C'、'D'
        char[] cc = {'A', 'B', 'C', 'D'};

        String s = "abcdefg";                // 声明String类型变量s并赋值为"abcdefg"

        // 创建java.util.Date对象，表示当前日期和时间
        java.util.Date o = new java.util.Date();  // 使用完整限定名创建Date对象

        // 调用println(boolean)重载版本，输出boolean值
        System.out.println(b);               // 输出：true

        // 调用println(char)重载版本，输出char值
        System.out.println(c);               // 输出：A

        // 调用println(int)重载版本，输出int值
        System.out.println(i);               // 输出：100

        // 调用println(long)重载版本，输出long值
        System.out.println(l);               // 输出：1000

        // 调用println(float)重载版本，输出float值
        System.out.println(f);               // 输出：99.0

        // 调用println(double)重载版本，输出double值
        System.out.println(d);               // 输出：999.0

        // 调用println()无参重载版本，输出一个空行（换行符）
        System.out.println();                // 输出空行

        // 调用println(char[])重载版本，输出字符数组的内容
        System.out.println(cc);              // 输出：ABCD（字符数组的特殊处理，输出每个字符）

        // 调用println(String)重载版本，输出字符串
        System.out.println(s);               // 输出：abcdefg

        // 调用println(Object)重载版本，输出对象的toString()方法返回值
        System.out.println(o);               // 输出：Date对象的字符串表示（如：Mon Jun 20 ...）
    }
}
