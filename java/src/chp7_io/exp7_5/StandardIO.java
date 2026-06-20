/**
 * 【功能说明】
 *   演示 Java 标准 I/O（控制台输入/输出）的基本用法。
 *   程序从标准输入（键盘 System.in）读取用户输入的内容，判断输入是否为整数：
 *   - 如果输入是整数，则输出该整数值
 *   - 如果输入不是整数（如普通文本），则输出原始字符串
 *   - 输入 "exit" 时程序结束
 *   通过 InputStreamReader 将 System.in（字节流）转换为字符流实现控制台文本输入。
 *
 * 【知识点】
 *   1. System.in：标准输入流（通常是键盘输入），属于 InputStream 类型（字节流）。
 *   2. InputStreamReader：字节流到字符流的"桥梁"，将 System.in 的字节转换为字符。
 *   3. BufferedReader：字符缓冲流，包装 InputStreamReader，提供高效的 readLine() 逐行读取。
 *   4. Integer.parseInt(String)：将字符串解析为 int 类型整数，若格式无效则抛出 NumberFormatException。
 *   5. NumberFormatException：数字格式异常，catch 捕获后使用 flag 标志位区分是否为数字。
 *   6. try-catch-finally：异常处理结构，finally 块总是执行（即使 try 中有 return）。
 *   7. equals() 方法：String 的比较必须使用 equals()，不能使用 ==（== 比较引用地址）。
 */
package chp7_io.exp7_5;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_5 子包中

import java.io.BufferedReader;               // 导入 BufferedReader 类，带缓冲的字符输入流，提供 readLine() 高效逐行读取
import java.io.IOException;                  // 导入 IOException 类，处理输入/输出操作异常
import java.io.InputStreamReader;            // 导入 InputStreamReader 类，将字节输入流转换为字符输入流（字节到字符的桥梁）

public class StandardIO {                    // 定义 StandardIO 公有类（标准输入输出演示）

    public static void main(String[] args) throws IOException {  // 程序入口 main 方法，声明抛出 IOException

        int i = 0;                           // 声明 int 变量 i，初始化为 0，用于存储解析后的整数值
        boolean flag;                        // 声明 boolean 变量 flag，用于标记输入是否为非数字（true=不是数字）
        String s;                            // 声明 String 变量 s，用于存储从控制台读取的原始输入字符串

        // 构建标准输入读取链：BufferedReader 包装 InputStreamReader 包装 System.in（字节流）
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in));  // 创建读取键盘输入的 BufferedReader

        System.out.println("请输入（exit退出）");     // 提示用户输入信息，"exit" 可退出程序

        try {                                // try 块开始，捕获可能抛出的 IOException
            s = in.readLine();               // readLine() 等待用户从键盘输入一行文本（按回车确认）

            while (!s.equals("exit")) {      // while 循环：当用户输入不是 "exit" 时持续处理
                try {                        // 内层 try 块，捕获 NumberFormatException
                    flag = false;            // 先将 flag 设为 false，假定输入可以转换为数字
                    i = Integer.parseInt(s); // 尝试将输入的字符串 s 解析为 int 类型整数
                } catch (NumberFormatException e) {  // 如果字符串格式无法解析为整数，捕获此异常
                    flag = true;             // 将 flag 设为 true，标记输入不是有效的数字
                    System.out.println("你输入的是：" + s);  // 输出原始字符串内容（不解析为数字）
                }                            // try-catch 块结束

                if (flag == false) {         // 如果 flag 仍为 false，说明输入成功解析为整数
                    System.out.println("整数" + i);  // 输出解析后的整数值
                }                            // if 语句结束

                s = in.readLine();           // 读取下一行用户输入，准备下一次循环处理
            }                                // while 循环结束

            System.out.println("程序结束！");     // 输出程序结束提示
            in.close();                      // 关闭 BufferedReader，释放系统资源

        } finally {                          // finally 块（无条件执行），此处为空

        }                                    // finally 块结束

    }                                        // main 方法结束

}                                            // StandardIO 类结束
