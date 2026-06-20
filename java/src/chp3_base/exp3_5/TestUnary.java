/**
 * 【功能说明】
 * 本程序演示 Java 中的一元运算符（Unary Operator）的使用。
 * 包括：一元负号（-）、一元正号（+）、前缀自增（++i）、后缀自增（i++）、
 * 前缀自减（--y）、后缀自减（y--）。
 * 程序通过一系列运算和输出展示了各运算符对变量值的具体影响，
 * 重点区分前/后缀自增/自减在"先使用后自增"与"先自增后使用"上的区别。
 *
 * 【知识点】
 * 1. 一元负号（-）：对操作数取负，改变符号位。
 * 2. 一元正号（+）：通常无实际作用，可用于将 byte/short 提升为 int。
 * 3. 前缀自增 ++i：先将 i 加 1，再使用 i 的值参与表达式。
 * 4. 后缀自增 i++：先使用 i 的原值参与表达式，再将 i 加 1。
 * 5. 前缀自减 --y：先将 y 减 1，再使用 y 的值。
 * 6. 后缀自减 y--：先使用 y 的原值，再将 y 减 1。
 * 7. 类型提升：byte 类型经一元正号运算后结果提升为 int。
 */
package chp3_base.exp3_5;                               // 包声明，该类位于 chp3_base.exp3_5 包中
public class TestUnary {                                 // 公共类 TestUnary
    public static void main(String[] args) {             // main 方法：Java 程序入口
        int a = 9;                     // 声明 int 变量 a 并初始化为 9
        int b = -a;                    // 一元负号运算符：对 a 取负，结果为 -9，赋值给 b
        byte bb = 9;                   // 声明 byte 变量 bb 并初始化为 9
        int ib = +bb;                  // 一元正号运算符：将 byte 提升为 int（值为 9），赋值给 ib
        int x = 4, y = 8;             // 声明两个 int 变量 x 和 y，分别初始化为 4 和 8
        int z;                         // 声明 int 变量 z，稍后使用
        int i = 0;                     // 声明 int 变量 i 并初始化为 0
        int j = i++;                   // 后缀自增：先将 i 的当前值（0）赋给 j，然后 i 自增为 1
                                       // 结果：j = 0, i = 1
        int k = ++j;                   // 前缀自增：先将 j 加 1（从 0 变为 1），再将加后的值赋给 k
                                       // 结果：j = 1, k = 1
        z = (x++) * (--y);             // (x++)：后缀自增，先使用 x 的当前值 4 参与乘法，再将 x 变为 5
                                       // (--y)：前缀自减，先将 y 减 1（从 8 变为 7），再使用 7 参与乘法
                                       // 结果为 z = 4 * 7 = 28
        System.out.println("a = " + a);           // 输出 a 的值（9）
        System.out.println("b = " + b);           // 输出 b 的值（-9）
        System.out.println("bb = " + bb);         // 输出 bb 的值（9）
        System.out.println("ib = " + ib);         // 输出 ib 的值（9，类型已从 byte 提升为 int）
        System.out.println("i = " + i);           // 输出 i 的值（经历了 i++，从 0 变为 1）
        System.out.println("j = " + j);           // 输出 j 的值（先被赋值为 0，后经 ++j 变为 1）
        System.out.println("k = " + k);           // 输出 k 的值（等于 ++j 的结果，即 1）
        System.out.println("x = " + x);           // 输出 x 的值（经历了 x++，从 4 变为 5）
        System.out.println("y = " + y);           // 输出 y 的值（经历了 --y，从 8 变为 7）
        System.out.println("z = " + z);           // 输出 z 的值（4 * 7 = 28）
    }                                                    // main 方法结束
}                                                        // 类定义结束
