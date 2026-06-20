/**
 * 【功能说明】
 *   演示 Java 中的字符流复制功能。程序以字符为单位读取源文件 farrago.txt 的内容，
 *   逐个字符写入到目标文件 outagainc.txt 中，实现文本文件的字符流复制。
 *   相较于 exp7_1 的 CopyBytes（字节流），本程序使用字符流，适合处理文本文件。
 *
 * 【知识点】
 *   1. 字符流 (Character Stream)：以 Reader/Writer 为基类的输入/输出流，按字符（2字节）处理数据。
 *   2. FileReader：文件字符输入流，以字符为单位从文件中读取文本数据（处理 Unicode 编码）。
 *   3. FileWriter：文件字符输出流，以字符为单位向文件中写入文本数据。
 *   4. read() 方法：每次读取一个字符（0~65535），到达文件末尾时返回 -1。
 *   5. write(int c) 方法：将指定的字符（低16位）写入输出流。
 *   6. 字符流 vs 字节流：字符流自动处理字符编码转换（如 Unicode <-> 本地编码），适合文本；字节流适合二进制文件。
 *   7. 路径表示：使用相对路径 "src\\chp7_io\\exp7_2\\..."，注意 Windows 系统下的路径分隔符转义。
 */
package chp7_io.exp7_2;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_2 子包中

import java.io.FileReader;                   // 导入 FileReader 类，用于从文件系统读取字符数据（字符输入流）
import java.io.FileWriter;                   // 导入 FileWriter 类，用于向文件系统写入字符数据（字符输出流）
import java.io.IOException;                  // 导入 IOException 类，用于处理输入/输出操作中发生的异常

public class Copy {                          // 定义 Copy 公有类（字符复制演示类）

    public static void main(String[] args) throws IOException {  // 程序入口 main 方法，声明抛出 IOException

        // 创建字符输入流和输出流，建立文件连接
        FileReader in = new FileReader("src\\chp7_io\\exp7_2\\farrago.txt");   // 创建 FileReader，以字符方式打开源文件（自动按系统默认编码解码）
        FileWriter out = new FileWriter("src\\chp7_io\\exp7_2\\outagainc.txt"); // 创建 FileWriter，指向目标文件（若不存在则新建）
        int c;                                                                   // 声明 int 变量 c，用于暂存每次读取到的字符

        // 循环读取源文件中的每个字符，写入目标文件
        while ((c = in.read()) != -1)   // read() 读取一个字符（0~65535），返回 -1 表示已读到文件末尾
           out.write(c);                // 将读取到的字符 c 写入输出流（只写入 int 的低 16 位，即一个 char）

        // 关闭流，释放系统资源
        in.close();                     // 关闭字符输入流，释放文件句柄
        out.close();                    // 关闭字符输出流，自动将缓冲区内容刷新（flush）到磁盘

    }                                    // main 方法结束

}                                        // Copy 类结束
