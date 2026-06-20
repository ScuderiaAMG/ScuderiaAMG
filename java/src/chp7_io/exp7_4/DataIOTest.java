/**
 * 【功能说明】
 *   演示 Java 数据流 (DataInputStream/DataOutputStream) 的读写操作。
 *   程序将一组商品数据（价格、数量、名称）通过 DataOutputStream 写入文件 invoice1.txt，
 *   再通过 DataInputStream 从同一文件中读取并恢复数据，最后计算订单总价并输出。
 *   Data 流可以按照 Java 基本数据类型的大小直接读写二进制数据，无需手动转换。
 *
 * 【知识点】
 *   1. DataOutputStream：数据输出流，以二进制格式写入 Java 基本类型（double/int/char 等）及字符串 (UTF)。
 *   2. DataInputStream：数据输入流，以二进制格式读取 Java 基本类型，与 DataOutputStream 写入顺序必须一致。
 *   3. writeDouble(double)：将 double 值按 8 字节 IEEE 754 格式写入输出流。
 *   4. writeInt(int)：将 int 值按 4 字节补码格式写入输出流。
 *   5. writeChar(int)：将 char 值按 2 字节 Unicode 格式写入输出流。
 *   6. writeUTF(String)：将字符串以 UTF-8 编码格式写入（先写 2 字节长度，再写字节内容）。
 *   7. 数据读写顺序一致性：读写的类型顺序必须完全匹配，否则数据会错乱或读取异常。
 *   8. 装饰器模式：DataOutputStream/DataInputStream 包装在 FileOutputStream/FileInputStream 之上，
 *      增强了字节流的处理能力。
 */
package chp7_io.exp7_4;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_4 子包中

import java.io.DataInputStream;              // 导入 DataInputStream 类，数据字节输入流，可读取 Java 基本数据类型
import java.io.DataOutputStream;             // 导入 DataOutputStream 类，数据字节输出流，可写入 Java 基本数据类型
import java.io.FileInputStream;              // 导入 FileInputStream 类，文件字节输入流，从文件读取字节
import java.io.FileOutputStream;             // 导入 FileOutputStream 类，文件字节输出流，向文件写入字节
import java.io.IOException;                  // 导入 IOException 类，处理输入/输出操作异常

public class DataIOTest {                    // 定义 DataIOTest 公有类（数据流读写测试）

    public static void main(String[] args) throws IOException {  // 程序入口 main 方法，声明抛出 IOException

        // ========== 第一部分：使用 DataOutputStream 写入数据 ==========
        // 将 DataOutputStream 包装在 FileOutputStream 之上，向文件写入基本数据类型
        DataOutputStream out = new DataOutputStream(new            // 创建 DataOutputStream 对象
                       FileOutputStream("src\\chp7_io\\exp7_4\\invoice1.txt"));  // 创建 FileOutputStream 指向输出文件

        // 准备三组要写入的数据：商品价格、数量、名称描述
        double[] prices = { 19.99, 9.99, 15.99, 3.99, 4.99 };     // 定义 double 类型数组，存储 5 件商品的价格
        int[] units = { 12, 8, 13, 29, 50 };                       // 定义 int 类型数组，存储 5 件商品的数量
        String[] descs = { "Java T-shirt", "Java Mug",             // 定义 String 类型数组，存储 5 件商品的名称
                            "Duke Juggling Dolls",
                            "Java Pin", "Java Key Chain" };

        // 使用 for 循环将价格、数量、描述依次写入文件，用 Tab 分隔符分隔不同字段
        for (int i = 0; i < prices.length; i ++) {                 // 遍历数组，i 从 0 到 4
            out.writeDouble(prices[i]);                             // 将第 i 个商品价格以 double（8 字节）写入文件
            out.writeChar('\t');                                    // 写入一个制表符 Tab（2 字节）作为字段分隔符
            out.writeInt(units[i]);                                 // 将第 i 个商品数量以 int（4 字节）写入文件
            out.writeChar('\t');                                    // 再次写入 Tab 分隔符
            out.writeUTF(descs[i]);                                 // 将第 i 个商品描述以 UTF-8 编码写入文件（先写长度，再写内容）
            out.writeChar('\t');                                    // 再次写入 Tab 分隔符（作为记录结束标记）
        }                                                           // for 循环结束
        out.close();                                                // 关闭 DataOutputStream（自动关闭底层 FileOutputStream）

        // ========== 第二部分：使用 DataInputStream 读取数据 ==========
        // 将 DataInputStream 包装在 FileInputStream 之上，从文件中以对应类型读取数据
        DataInputStream in = new DataInputStream(new                // 创建 DataInputStream 对象
                     FileInputStream("src\\chp7_io\\exp7_4\\invoice1.txt"));  // 创建 FileInputStream 打开刚才写入的文件

        double price;                       // 声明 double 变量 price，用于存储读取到的价格
        int unit;                           // 声明 int 变量 unit，用于存储读取到的数量
        String desc;                        // 声明 String 变量 desc，用于存储读取到的商品名称
        double total = 0.0;                 // 声明 double 变量 total，初始化为 0.0，用于累计订单总金额

        // 注意：读取的顺序必须与写入时的顺序完全一致
        for (int i = 0; i < prices.length; i ++) {                 // 循环 5 次，读取 5 条记录
                price = in.readDouble();                            // 读取 8 个字节转换为 double 类型（价格）
                in.readChar();                                      // 读取 2 个字节，跳过 Tab 分隔符
                unit = in.readInt();                                // 读取 4 个字节转换为 int 类型（数量）
                in.readChar();                                      // 读取 2 个字节，跳过 Tab 分隔符
                desc = in.readUTF();                                // 读取 UTF-8 编码字符串（先读 2 字节长度，再读内容）
                in.readChar();                                      // 读取 2 个字节，跳过结尾 Tab 分隔符

                // 将读取到的数据格式化输出到控制台
                System.out.println("You've ordered " +              // 输出 "您已订购" 信息
                        unit + " units of " +                       // 输出数量 + "件"
                        desc + " at $" + price);                    // 输出商品名称 + "单价为"
                total = total + unit * price;                       // 累计计算订单总金额：单价 * 数量
        }                                                           // for 循环结束

        System.out.println("For a TOTAL of: $" + total);           // 输出订单总金额
        in.close();                                                 // 关闭 DataInputStream（自动关闭底层 FileInputStream）

    }                                                               // main 方法结束

}                                                                   // DataIOTest 类结束
