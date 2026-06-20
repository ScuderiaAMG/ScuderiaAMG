/*
 * ============================================================
 * 【功能说明】
 * 本程序是对 exp6_1 的改进版本，演示了如何使用 try-catch-finally
 * 结构捕获并处理数组越界异常（ArrayIndexOutOfBoundsException）。
 * 程序同样定义了一个长度为3的字符串数组并用 while(i<4) 循环访问，
 * 当 i=3 时发生越界异常，但被 catch 块捕获并打印提示信息后
 * 通过 break 跳出循环，程序最终可以正常结束。
 * finally 块中的信息每次循环都会打印，展示了 finally 无论
 * 是否发生异常都会执行的特性。
 *
 * 【知识点】
 * 1. ArrayIndexOutOfBoundsException：数组下标越界异常
 *    （IndexOutOfBoundsException 的子类）
 * 2. try-catch-finally 结构在循环中的使用
 * 3. e.getMessage() 获取异常消息（本例未使用但有e参数）
 * 4. finally 块的确定性执行特性 —— "This is always printed"
 * 5. break 语句在 catch 块中用于跳出循环
 * 6. 通过异常处理使程序从错误中恢复并继续执行
 * ============================================================
 */
package chp6_exception.exp6_4;                             // 声明包路径，属于第6章异常处理实验4
public class HelloWorld2 {                                  // 定义公开类HelloWorld2
    public static void main(String args[ ]) {               // 程序入口点，String数组参数接收命令行参数
        int i = 0;                                          // 初始化循环计数器i为0
        String greetings[ ] = { "Hello World!", "Hello!",   // 声明并静态初始化字符串数组，包含3个元素
                "HELLO WORLD!!" };                          // 数组元素分别为"Hello World!"、"Hello!"、"HELLO WORLD!!"
        while (i < 4) {                                     // while循环，条件i<4；数组长度为3，第4次循环必然越界
            try {                                           // try块开始：监视可能抛出异常的代码
                System.out.println(greetings[i]);           // 访问数组第i个元素并打印；当i=3时抛出ArrayIndexOutOfBoundsException
                i++;                                        // 计数器自增1（仅当未发生异常时才执行）
            } catch (ArrayIndexOutOfBoundsException e) {    // 捕获数组下标越界异常
                System.out.println("Caught ArrayIndexOutOfBoundsException"); // 打印捕获到异常的提示信息
                break;                                      // break跳出while循环，终止循环执行
            } finally {                                     // finally块：无论是否发生异常，每次循环都会执行
                System.out.println("This is always printed"); // 打印"这条信息总是会被打印"，展示finally的确定性执行
            }                                               // finally块结束
        }                                                   // while循环结束
    }                                                       // main方法结束
}                                                           // 类定义结束
