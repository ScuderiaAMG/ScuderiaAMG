/**
 * 【功能说明】
 *   演示 Java 管道流（PipedReader/PipedWriter）与多线程结合的典型应用。
 *   程序从 words.txt 文件中读取单词列表，通过管道流将数据传递给多个线程进行流水线处理：
 *   先 reverse() 将每个单词反转 -> sort() 对反转后的单词按字典序排序 ->
 *   再 reverse() 将排序后的单词再次反转，从而实现"按单词末尾字母（押韵）排序"的效果。
 *   处理流程：reverse -> sort -> reverse，利用反转-排序-再反转技巧实现按后缀排序。
 *
 * 【知识点】
 *   1. 管道流 (Piped Streams)：PipedWriter 和 PipedReader 配对使用，在线程间传递数据（无需中间文件）。
 *   2. 流水线设计模式：多个处理阶段通过管道连接，每个阶段在不同线程中并行处理。
 *   3. 线程间通信：一个线程通过 PipedWriter 写入数据，另一个线程通过关联的 PipedReader 读取数据。
 *   4. 函数式组合：reverse(sort(reverse(words))) 将多个处理方法嵌套组合，形成处理流水线。
 *   5. 多态返回类型：方法返回 Reader 类型（抽象父类），实际返回的是 PipedReader 实例。
 *   6. 反转-排序-再反转技巧：按单词后缀排序 = 反转所有单词 -> 排序 -> 再次反转。
 *   7. start() 启动线程：调用 start() 而非 run()，JVM 会新建线程并自动执行 run() 方法体。
 */
package chp7_io.exp7_3;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_3 子包中

import java.io.BufferedReader;               // 导入 BufferedReader 类，带缓冲的字符输入流，提供 readLine() 高效逐行读取
import java.io.FileReader;                   // 导入 FileReader 类，文件字符输入流，从文件读取字符数据
import java.io.IOException;                  // 导入 IOException 类，处理输入/输出操作异常
import java.io.PipedReader;                  // 导入 PipedReader 类，管道字符输入流，与 PipedWriter 配合实现线程间通信
import java.io.PipedWriter;                  // 导入 PipedWriter 类，管道字符输出流，与 PipedReader 配合实现线程间通信
import java.io.PrintWriter;                  // 导入 PrintWriter 类，格式化字符输出流，提供 println() 便捷输出方法
import java.io.Reader;                       // 导入 Reader 类，字符输入流的顶层抽象基类

public class RhymingWords {                  // 定义 RhymingWords 公有类（押韵词排序主程序）

    public static void main(String[] args) throws IOException {  // 程序入口 main 方法，声明抛出 IOException

        // 第一步：打开源文件，创建 FileReader
        FileReader words = new FileReader("src\\chp7_io\\exp7_3\\words.txt");  // 创建 FileReader 读取单词源文件

        // 第二步：构建流水线处理链——反转 -> 排序 -> 再反转（按尾字母排序的技巧）
        Reader rhymedWords = reverse(sort(reverse(words)));  // 嵌套调用：先反转 -> 排序 -> 再反转，返回最终的 Reader

        // 第三步：包装为 BufferedReader，逐行读取处理结果并输出到控制台
        BufferedReader in = new BufferedReader(rhymedWords);  // 将最终输出的 Reader 包装为 BufferedReader
        String input;                                          // 声明 String 变量 input，暂存每次读取的一行

        while ((input = in.readLine()) != null)                // readLine() 逐行读取，返回 null 表示读取完毕
            System.out.println(input);                         // 将处理后的每一行输出到标准输出（控制台）
        in.close();                                            // 关闭 BufferedReader，释放资源

    }                                                          // main 方法结束

    /**
     * 反转处理方法：将 Reader 中的每行数据逐行反转输出
     * @param source 源字符输入流
     * @return 管道输入流（PipedReader），另一端连接的 ReverseThread 线程正在处理数据
     * @throws IOException IO 操作异常
     */
    public static Reader reverse(Reader source) throws IOException {  // 静态方法 reverse，接收一个 Reader，返回一个 Reader

        BufferedReader in = new BufferedReader(source);       // 将传入的 source 包装为 BufferedReader 以提高读取效率

        PipedWriter pipeOut = new PipedWriter();              // 创建管道输出流（写入端）
        PipedReader pipeIn = new PipedReader(pipeOut);        // 创建管道输入流（读取端），并与 pipeOut 连接配对
        PrintWriter out = new PrintWriter(pipeOut);           // 将 pipeOut 包装为 PrintWriter，方便使用 println()

        new ReverseThread(out, in).start();                   // 创建 ReverseThread 线程对象（传入输入/输出流），并启动线程

        return pipeIn;                                        // 返回管道输入流，供下游处理阶段读取数据

    }                                                          // reverse 方法结束

    /**
     * 排序处理方法：将 Reader 中的每行数据按字典序排序后输出
     * @param source 源字符输入流
     * @return 管道输入流（PipedReader），另一端连接的 SortThread 线程正在处理数据
     * @throws IOException IO 操作异常
     */
    public static Reader sort(Reader source) throws IOException {  // 静态方法 sort，接收一个 Reader，返回一个 Reader

        BufferedReader in = new BufferedReader(source);       // 将传入的 source 包装为 BufferedReader 提高读取效率

        PipedWriter pipeOut = new PipedWriter();              // 创建管道输出流（写入端）
        PipedReader pipeIn = new PipedReader(pipeOut);        // 创建管道输入流（读取端），并与 pipeOut 配对连接
        PrintWriter out = new PrintWriter(pipeOut);           // 将 pipeOut 包装为 PrintWriter，方便使用 println()

        new SortThread(out, in).start();                      // 创建 SortThread 线程对象（传入输入/输出流），并启动线程

        return pipeIn;                                        // 返回管道输入流，供下游处理阶段读取数据

    }                                                          // sort 方法结束

}                                                              // RhymingWords 类结束
