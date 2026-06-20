/**
 * 【功能说明】
 *   演示 RandomAccessFile 随机访问文件的用法。
 *   程序以只读模式 ("r") 打开自身源代码文件 (RandomAccessTest.java)，
 *   逐行读取并输出到控制台，同时通过 getFilePointer() 获取和监控当前文件指针位置。
 *   与普通流不同，RandomAccessFile 可以自由移动文件指针，实现随机读写。
 *
 * 【知识点】
 *   1. RandomAccessFile：支持随机访问的文件读写类，可在文件中任意位置进行读写操作。
 *   2. 文件模式 (mode)："r" 表示只读，"rw" 表示读写，"rws"/"rwd" 表示同步读写。
 *   3. length()：获取文件的长度（字节数），作为循环的结束条件。
 *   4. readLine()：读取文件中的一行文本（以换行符为界），返回 String，读到末尾返回 null。
 *   5. getFilePointer()：获取当前文件指针的位置（从文件开头算起的字节偏移量），用于跟踪读取进度。
 *   6. 文件指针：RandomAccessFile 维护一个可移动的文件指针，默认初始位置为文件开头（偏移量 0）。
 *   7. 读取自身源码：通过打开自身 .java 文件展示文件的自我读取能力。
 *   8. throws Exception：直接声明抛出所有异常（简化代码，将异常处理交给 JVM）。
 */
package chp7_io.exp7_7;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_7 子包中

import java.io.RandomAccessFile;             // 导入 RandomAccessFile 类，支持随机访问文件（可定位到任意位置读写）

public class RandomAccessTest {              // 定义 RandomAccessTest 公有类（随机访问文件演示）

    public static void main(String args[]) throws Exception {  // 程序入口 main 方法，声明抛出所有异常

        long filePoint = 0;                  // 声明 long 变量 filePoint，初始化为 0，用于记录文件指针位置
        String s;                            // 声明 String 变量 s，用于暂存读取到的每行文本

        // 创建 RandomAccessFile 对象，以只读模式 ("r") 打开当前源代码文件
        RandomAccessFile file = new RandomAccessFile("src\\chp7_io\\exp7_7\\RandomAccessTest.java", "r");
        // RandomAccessFile 第一个参数是文件路径，第二个参数是访问模式

        long fileLength = file.length();     // 调用 length() 方法获取文件的总长度（字节数）

        // 当文件指针位置小于文件总长度时，循环读取文件内容
        while (filePoint < fileLength) {     // 文件指针 filePoint < 文件长度 fileLength 时继续读取
            s = file.readLine();             // readLine() 从当前指针位置开始，读取到行尾（遇到 '\n' 或 '\r\n' 为止）
            System.out.println(s);           // 将读取到的行输出到标准输出（控制台）
            filePoint = file.getFilePointer();  // 获取当前文件指针的位置（已读取的字节数），更新到 filePoint 变量
        }                                    // while 循环结束

        file.close();                        // 关闭 RandomAccessFile，释放文件句柄和系统资源

    }                                        // main 方法结束

}                                            // RandomAccessTest 类结束
