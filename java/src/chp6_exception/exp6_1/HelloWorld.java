/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了Java中数组越界访问所引发的运行时异常
 * (ArrayIndexOutOfBoundsException)。
 * 程序定义了一个长度为3的字符串数组，但循环条件设置为 i<4，
 * 导致循环第4次访问数组元素 greetings[3] 时发生越界异常，
 * 程序因此非正常终止，最后的 "Normal ended." 不会被执行。
 * 该示例展示了未处理异常时程序的默认行为——异常传播至JVM
 * 后导致线程终止。
 *
 * 【知识点】
 * 1. 数组声明与初始化：String[] 静态初始化语法
 * 2. 数组下标从0开始，最大下标为 length-1
 * 3. ArrayIndexOutOfBoundsException 运行时异常
 *    （RuntimeException 的子类，无需显式捕获或声明）
 * 4. 未捕获异常导致程序提前终止的机制
 * 5. main 方法的签名：public static void main(String args[])
 * ============================================================
 */
package chp6_exception.exp6_1;                             // 声明包路径，属于第6章异常处理实验1
public class HelloWorld {                                  // 定义公开类HelloWorld
    public static void main(String args[ ]) {               // 程序入口点，String数组参数接收命令行参数
        int i = 0;                                          // 初始化循环计数器i为0
        String greetings[ ] = { "Hello World!", "Hello!",   // 声明并静态初始化字符串数组，包含3个元素
                "HELLO WORLD!!" };                           // 数组元素分别为"Hello World!"、"Hello!"、"HELLO WORLD!!"
        while (i < 4) {                                     // while循环，条件i<4；数组长度为3，最大下标为2，因此第4次循环会越界
            System.out.println(greetings[i]);               // 访问数组第i个元素并打印；当i=3时抛出ArrayIndexOutOfBoundsException
            i++;                                            // 计数器自增1
        }                                                   // while循环结束
        System.out.println("Normal ended.");                 // 打印"Normal ended."表示程序正常结束；由于异常未捕获，此行不会执行
    }                                                       // main方法结束
}                                                           // 类定义结束
