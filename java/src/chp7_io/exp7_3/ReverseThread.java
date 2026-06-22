/**
 * 【功能说明】
 *   定义一个线程类，从 BufferedReader 中逐行读取字符串，将每个字符串反转后通过 PrintWriter 输出。
 *   通过继承 Thread 类实现多线程，演示了线程的创建、运行和 I/O 流在多个线程之间的传递与复用。
 *   本类配合 RhymingWords.java（主程序）和 SortThread.java（排序线程）完成"押韵词"处理流程。
 *
 * 【知识点】
 *   1. 继承 Thread 类：自定义线程类通过 extends Thread 创建，重写 run() 方法定义线程执行体。
 *   2. BufferedReader：带缓冲的字符输入流，通过 readLine() 逐行读取文本，效率高于逐个字符读取。
 *   3. PrintWriter：格式化字符输出流，println() 自动追加行分隔符，flush() 强制刷新缓冲区。
 *   4. 流传递：通过构造函数将 I/O 流对象传入线程，实现线程间的流复用（管道通信模式）。
 *   5. StringBuffer：线程安全的可变字符序列，适合在字符串反转等场景中频繁拼接操作。
 *   6. 字符串反转算法：从最后一个字符向前遍历，依次追加到 StringBuffer 中拼接成反转字符串。
 *   7. 异常处理：try-catch 捕获 IOException，使用 System.err.println() 输出错误信息到标准错误流。
 */
package chp7_io.exp7_3;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_3 子包中

import java.io.BufferedReader;               // 导入 BufferedReader 类，带缓冲的字符输入流，提供高效的 readLine() 方法
import java.io.IOException;                  // 导入 IOException 类，用于处理输入/输出操作中发生的异常
import java.io.PrintWriter;                  // 导入 PrintWriter 类，格式化文本输出流，提供 println() 等便捷方法

public class ReverseThread extends Thread {  // 定义 ReverseThread 类，继承自 Thread，成为一个自定义线程类

    private PrintWriter out = null;          // 声明 PrintWriter 类型成员变量 out（输出流），初始化为 null
    private BufferedReader in = null;        // 声明 BufferedReader 类型成员变量 in（输入流），初始化为 null

    /**
     * 构造函数：接收一个 PrintWriter 和一个 BufferedReader 作为参数
     * @param out  输出流，用于写入反转后的字符串
     * @param in   输入流，用于读取待反转的源字符串
     */
    public ReverseThread(PrintWriter out, BufferedReader in) {  // 带参构造函数，传入输入/输出流
        this.out = out;                     // 将参数 out 赋值给成员变量 this.out
        this.in = in;                       // 将参数 in 赋值给成员变量 this.in
    }                                       // 构造函数结束

    // 重写 Thread 类的 run() 方法，定义线程的执行体
    public void run() {                     // 当线程 start() 后，JVM 自动调用此方法
        if (out != null && in != null) {    // 检查输入流和输出流是否都已正确初始化
            try {                           // try 块开始，捕获可能抛出的 IOException
                String input;               // 声明 String 变量 input，暂存每次读取的一行文本
                while ((input = in.readLine()) != null) {  // readLine() 读取一行（不含换行符），返回 null 表示已无更多数据
                    out.println(reverseIt(input));          // 调用 reverseIt() 反转字符串，通过 println() 输出反转后的结果
                    out.flush();                             // 强制刷新输出缓冲区，确保数据立即写入目的地
                }                                            // while 循环结束
                out.close();                 // 读取完毕后关闭输出流，释放资源
            } catch (IOException e) {        // 捕获 IO 操作中发生的异常
                System.err.println("ReverseThread run: " + e);  // 将异常信息打印到标准错误输出流
            }                                // catch 块结束
        }                                    // if 语句结束
    }                                        // run() 方法结束

    /**
     * 反转字符串的私有辅助方法
     * @param source 源字符串
     * @return 反转后的字符串
     */
    private String reverseIt(String source) {               // 定义私有方法 reverseIt，参数为源字符串，返回反转后结果
        int i, len = source.length();                       // 声明索引变量 i 和字符串长度变量 len（初始化为源字符串长度）
        StringBuffer dest = new StringBuffer(len);          // 创建 StringBuffer 对象，初始容量设为源字符串长度（避免扩容）

        for (i = (len - 1); i >= 0; i--)                    // for 循环：从最后一个字符的索引 (len-1) 开始，递减遍历到 0
            dest.append(source.charAt(i));                  // 将当前位置的字符追加到 dest 中，实现反转拼接
        return dest.toString();                             // 将 StringBuffer 转换为 String 对象并返回
    }
}