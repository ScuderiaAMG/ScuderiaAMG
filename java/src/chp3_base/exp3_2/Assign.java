/**
 * 【功能说明】
 * 本程序演示 Java 中各种基本数据类型变量的声明、赋值和输出操作。
 * 涵盖了 int（整型）、float（单精度浮点型）、double（双精度浮点型）、
 * boolean（布尔型）、char（字符型）以及引用类型 String 的变量声明与初始化。
 * 程序依次为每个变量赋值，然后通过 System.out.println() 将它们输出到控制台。
 *
 * 【知识点】
 * 1. Java 基本数据类型：int（4字节）、float（4字节，需加 f/F 后缀）、
 *    double（8字节）、boolean（true/false）、char（16位 Unicode 字符）。
 * 2. 引用类型 String：本质上是 java.lang.String 类的对象，非基本类型。
 * 3. 变量声明与初始化分离（先声明后赋值）。
 * 4. 浮点数字面量默认是 double 类型，给 float 赋值须加 f/F 后缀。
 * 5. 本章核心：变量 — 类型、声明、赋值、初始化。
 */
package chp3_base.exp3_2;                               // 包声明，指明该类位于 chp3_base.exp3_2 包中
public class Assign{                                     // 公共类 Assign，类名与文件名一致
    public static void main (String[] args){             // main 方法：Java 程序的入口
        int x,y;                    // 声明两个 int 类型变量 x 和 y，此时尚未赋值（默认值不可用）
        float z=3.414f;             // 声明 float 类型变量 z 并初始化为 3.414（注意 float 字面量必须加 f 后缀）
        double w=3.1415;            // 声明 double 类型变量 w 并初始化为 3.1415（double 是浮点数的默认类型）
        boolean truth=true;         // 声明 boolean 类型变量 truth 并初始化为 true（布尔值只有 true/false）
        char c;                     // 声明 char 类型变量 c，尚未赋值
        String str;                 // 声明 String 引用类型变量 str，尚未赋值（默认值为 null）
        String str1="bye";          // 声明 String 引用类型变量 str1 并初始化为字符串 "bye"
        c='A';                      // 为 char 变量 c 赋值为字符 'A'（字符字面量使用单引号）
        str="Hi out there";         // 为 String 变量 str 赋值为字符串 "Hi out there"（字符串使用双引号）
        x=6;                        // 为 int 变量 x 赋值为 6
        y=1000;                     // 为 int 变量 y 赋值为 1000
        System.out.println("x = "+x);       // 输出 x 的值，字符串拼接运算符 + 将 int 转为 String
        System.out.println("y = "+y);       // 输出 y 的值
        System.out.println("z = "+z);       // 输出 z 的值
        System.out.println("w = "+w);       // 输出 w 的值
        System.out.println("truth = "+truth);   // 输出 truth 的值（布尔值输出为 "true" 或 "false"）
        System.out.println("c = "+c);       // 输出 c 的值（char 类型拼接时先转为字符串）
        System.out.println("str = "+str);   // 输出 str 的值（字符串变量直接拼接）
        System.out.println("str1 = "+str1); // 输出 str1 的值
    }                               // main 方法结束
}                                   // 类定义结束
