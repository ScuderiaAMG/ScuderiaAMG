/**
 * 【功能说明】
 *   演示 Java NIO (New IO / Non-blocking IO) 的通道 (Channel) 和缓冲区 (Buffer) 机制。
 *   程序通过 FileChannel（文件通道）从源文件 farrago.txt 读取数据到 ByteBuffer 缓冲区，
 *   再将缓冲区中的数据写入目标文件 outagain.txt，实现文件的复制。
 *   与传统的字节流复制（exp7_1 的 CopyBytes）相比，NIO 方式效率更高，
 *   因为通道直接与操作系统底层 I/O 交互，减少了内存拷贝次数。
 *
 * 【知识点】
 *   1. NIO (New IO)：Java 1.4 引入的新 I/O 库，基于通道 (Channel) 和缓冲区 (Buffer)。
 *   2. FileChannel：文件通道，连接到文件的 I/O 通道，支持读取、写入、映射等操作。
 *   3. ByteBuffer：字节缓冲区，是 NIO 中的数据传输容器，位于通道之间。
 *   4. allocate(int capacity)：分配指定容量（字节数）的 ByteBuffer 缓冲区。
 *   5. read(ByteBuffer)：从通道读取数据到缓冲区，返回读取的字节数，-1 表示文件末尾。
 *   6. flip()：反转缓冲区——将 limit 设为当前位置（已读数据量），position 设为 0，
 *      使缓冲区从"写入模式"切换到"读取模式"。
 *   7. write(ByteBuffer)：将缓冲区中的数据写入通道，从 position 到 limit 之间的数据。
 *   8. clear()：清空缓冲区——将 position 设为 0，limit 设为 capacity，
 *      使缓冲区从"读取模式"切换回"写入模式"。
 *   9. 获取通道：通过 FileInputStream.getChannel() 获取只读通道，
 *      通过 FileOutputStream.getChannel() 获取只写通道。
 *   10. NIO 优势：通道直接与操作系统内核交互（系统调用），减少用户态与内核态的数据拷贝次数。
 */
package chp7_io.exp7_12;                     // 声明包路径，位于 chp7_io 实验包下的 exp7_12 子包中

import java.io.FileInputStream;              // 导入 FileInputStream 类，文件字节输入流，从文件读取字节数据
import java.io.FileOutputStream;             // 导入 FileOutputStream 类，文件字节输出流，向文件写入字节数据
import java.io.IOException;                  // 导入 IOException 类，处理输入/输出操作异常
import java.nio.ByteBuffer;                  // 导入 ByteBuffer 类，NIO 字节缓冲区，用于在通道间传输数据
import java.nio.channels.FileChannel;        // 导入 FileChannel 类，NIO 文件通道，提供高效的文件 I/O 操作

public class CopyBytesWithChannel {          // 定义 CopyBytesWithChannel 公有类（NIO 通道复制演示类）

    private static final int BSIZE = 1024;   // 定义常量 BSIZE = 1024（1KB），表示缓冲区大小（字节数）

    public static void main(String[] args) throws IOException {  // 程序入口 main 方法，声明抛出 IOException

        // 第一步：创建传统文件流，用于获取文件通道
        FileInputStream inStream = new FileInputStream("src\\chp7_io\\exp7_12\\farrago.txt");
        // 创建 FileInputStream，打开源文件（用于获取输入通道）

        FileOutputStream outStream = new FileOutputStream("src\\chp7_io\\exp7_12\\outagain.txt");
        // 创建 FileOutputStream，创建/覆盖目标文件（用于获取输出通道）

        // 第二步：通过流的 getChannel() 方法获取文件通道
        FileChannel inChannel = inStream.getChannel();   // 获取读取通道（与源文件关联，只读）
        FileChannel outChannel = outStream.getChannel(); // 获取写入通道（与目标文件关联，只写）

        // 第三步：分配缓冲区（1KB），作为数据传输的中转容器
        ByteBuffer buffer = ByteBuffer.allocate(BSIZE);  // 在堆外或堆上分配 1024 字节的缓冲区

        // 第四步：循环读取数据到缓冲区，再从缓冲区写入目标通道
        while ((inChannel.read(buffer)) != -1) {         // 从 inChannel 读取数据填充 buffer，返回读取字节数，-1 表示文件末尾
           buffer.flip();                 // flip()：将 buffer 从"写入模式"切换到"读取模式"
                                           // limit = 原 position（已读数据量），position = 0
           outChannel.write(buffer);       // 将 buffer 中的数据（从 position 到 limit）写入 outChannel
           buffer.clear();                 // clear()：将 buffer 从"读取模式"切换回"写入模式"
                                           // position = 0，limit = capacity，准备下一次读取
        }                                  // while 循环结束

        // 第五步：关闭传统流（通道将随之关闭）
        inStream.close();                  // 关闭输入流，释放文件句柄及关联的 inChannel
        outStream.close();                 // 关闭输出流，释放文件句柄及关联的 outChannel

    }                                      // main 方法结束

}                                          // CopyBytesWithChannel 类结束
