/**
 * 【功能说明】
 * 本程序演示了Java中自动装箱（Auto-boxing）和自动拆箱（Auto-unboxing）机制。
 * Integer是int基本类型的包装类（Wrapper Class）。程序创建了两个Integer对象，
 * 直接通过字面量赋值（自动装箱），然后使用compareTo()方法比较大小，
 * 并直接对Integer对象使用算术运算符进行求和运算（自动拆箱）。
 *
 * 【知识点】
 * 1. 自动装箱（Auto-boxing）：JDK 5引入，基本类型自动转换为对应的包装类对象
 *    int -> Integer，如：Integer x = 22（编译器自动转换为Integer.valueOf(22)）
 * 2. 自动拆箱（Auto-unboxing）：包装类对象自动转换为基本类型
 *    Integer -> int，如：x + y 中的x和y自动拆箱为int进行算术运算
 * 3. Integer.compareTo()：比较两个Integer的大小，返回负数、0或正数
 * 4. 包装类（Wrapper Class）：为基本类型提供的对象表示，如Integer、Double、Boolean等
 * 5. 条件-赋值组合表达式：(c = x.compareTo(y)) == 0 先赋值再比较
 * 6. 嵌套if-else：根据compareTo的返回值判断大于、小于或等于关系
 * 7. 算术运算中的自动拆箱：x + y自动拆箱为int后进行加法运算，结果再自动装箱回Integer用于字符串拼接
 * 8. 字符串拼接中的自动装箱：任何对象与字符串使用+连接时自动调用toString()方法
 */
package chp5_advanced.exp5_20;                             // 声明包路径，该文件位于chp5_advanced.exp5_20包中

public class AutoBoxingTest {                              // 主类（public），测试自动装箱和拆箱机制
    public static void main(String args[]) {               // 主方法：程序执行的入口点
        Integer x, y;                                      // 声明两个Integer包装类引用变量
        int c;                                             // 声明基本类型int变量c，用于存储比较结果

        x = 22;                                            // 自动装箱：基本类型int值22自动转换为Integer对象（编译器调用Integer.valueOf(22)）
        y = 15;                                            // 自动装箱：基本类型int值15自动转换为Integer对象

        if ((c = x.compareTo(y)) == 0)                     // 调用compareTo比较x和y：将比较结果赋给c，然后判断是否为0（相等）
            System.out.println("x is equal to y");         // 如果c == 0，输出"x等于y"
        else                                               // 否则（c != 0）
            if (c < 0)                                     // 如果c < 0，表示x小于y
                System.out.println("x is less than y");    // 输出"x小于y"
            else                                           // 否则（c > 0），表示x大于y
                System.out.println("x is greater than y"); // 输出"x大于y"

        System.out.println("The sum of x and y is " + (x + y)); // x+y中的x和y自动拆箱为int进行加法运算，结果自动装箱后与字符串拼接输出
    }
}
