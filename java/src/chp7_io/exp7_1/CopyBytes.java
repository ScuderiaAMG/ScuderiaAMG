/**
 * 【功能说明】
 *   演示 Java 中最基本的字节流复制功能。程序以字节为单位读取源文件 farrago.txt 的内容，
 *   逐字节写入到目标文件 outagainb.txt 中，实现文件的精确复制。
 *
 * 【知识点】
 *   1. 字节流 (Byte Stream)：以 InputStream/OutputStream 为基类的输入/输出流，按字节处理数据。
 *   2. FileInputStream：文件字节输入流，以字节为单位从文件中读取数据。
 *   3. FileOutputStream：文件字节输出流，以字节为单位向文件中写入数据。
 *   4. read() 方法：每次读取一个字节（0-255），到达文件末尾时返回 -1 作为结束标志。
 *   5. write(int b) 方法：将指定的字节（低8位）写入输出流。
 *   6. 异常声明 throws IOException：将可能发生的 IO 异常抛给 JVM 处理（简化错误处理）。
 *   7. 流的关闭：使用完流后必须调用 close() 方法释放系统资源。
 *   8. 路径表示：使用相对路径 "src\\chp7_io\\exp7_1\\..."，注意 Windows 下的双反斜杠转义。
 */
package chp7_io.exp7_1;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_1 子包中

import java.io.File;                         // 导入 File 类，用于表示文件或目录路径的抽象表示
import java.io.FileInputStream;              // 导入 FileInputStream 类，用于从文件系统读取字节数据（字节输入流）
import java.io.FileOutputStream;             // 导入 FileOutputStream 类，用于向文件系统写入字节数据（字节输出流）
import java.io.IOException;                  // 导入 IOException 类，用于处理输入/输出操作中发生的异常

public class CopyBytes {                     // 定义 CopyBytes 公有类（字节复制演示类）

    public static void main(String[] args) throws IOException {  // 程序入口 main 方法，声明抛出 IOException

        // 第一步：创建 File 对象，表示目标输出文件
        File outputFile = new File("src\\chp7_io\\exp7_1\\outagainb.txt");  // 创建 File 对象指向目标文件路径

        // 第二步：创建输入流和输出流，建立文件连接通道
        FileInputStream in = new FileInputStream("src\\chp7_io\\exp7_1\\farrago.txt");   // 创建 FileInputStream，以只读方式打开源文件
        FileOutputStream out = new FileOutputStream(outputFile);                         // 创建 FileOutputStream，指向目标文件（若不存在则新建，存在则覆盖）
        int c;                                                                           // 声明 int 变量 c，用于暂存每次读取到的字节

        // 第三步：循环读取源文件中的每个字节，写入目标文件
        while ((c = in.read()) != -1)   // read() 读取一个字节（0~255），返回 -1 表示已读到文件末尾；将读取的字节赋值给 c 同时与 -1 比较
           out.write(c);                // 将读取到的字节 c 写入输出流（只写入 int 的低 8 位，即一个字节）

        // 第四步：关闭流，释放系统资源
        in.close();                     // 关闭输入流，释放文件句柄和相关系统资源
        out.close();                    // 关闭输出流，同时将缓冲区中残留的数据刷新（flush）到磁盘

    }                                    // main 方法结束

}                                        // CopyBytes 类结束
