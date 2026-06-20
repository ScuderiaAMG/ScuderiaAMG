/**
 * 【功能说明】
 *   演示 Java 对象反序列化 (Deserialization) 机制。程序从 date.ser 文件中读取字节流，
 *   通过 ObjectInputStream 的反序列化功能恢复出原始的 Date 对象。
 *   与 exp7_8 的 SerializeDate 程序配套使用，展示了序列化的完整逆过程。
 *   注意：反序列化时文件路径包含包路径（不同于 SerializeDate 的相对根目录路径），
 *   表明了两个实验包可能各自独立运行。
 *
 * 【知识点】
 *   1. 反序列化 (Deserialization)：将字节序列恢复为 Java 对象的过程，是序列化的逆操作。
 *   2. ObjectInputStream：对象输入流，通过 readObject() 从字节流中读取并重建 Java 对象。
 *   3. readObject()：读取并反序列化一个对象，返回 Object 类型，需要强制类型转换为具体类型。
 *   4. 强制类型转换：(Date) s.readObject() 将反序列化的 Object 向下转型为 Date。
 *   5. 异常处理：catch(Exception e) 捕获所有异常（包括 ClassNotFoundException、IOException 等）。
 *   6. 序列化兼容性：反序列化时必须保证类定义与序列化时完全兼容（相同 serialVersionUID）。
 *   7. e.printStackTrace()：打印异常的完整堆栈跟踪信息，包含异常链中每个方法的调用位置。
 *   8. 文件路径差异：SerializeDate 使用相对路径 "date.ser"，UnSerializeDate 使用相对路径
 *      "src\\chp7_io\\exp7_9\\date.ser"，说明运行时的当前工作目录不同。
 */
package chp7_io.exp7_9;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_9 子包中

import java.io.FileInputStream;              // 导入 FileInputStream 类，文件字节输入流，从文件中读取字节数据
import java.io.ObjectInputStream;            // 导入 ObjectInputStream 类，对象输入流，可从字节流中反序列化恢复 Java 对象
import java.util.Date;                       // 导入 Date 类，用于声明反序列化恢复后的 Date 类型变量

public class UnSerializeDate {               // 定义 UnSerializeDate 公有类（反序列化日期演示类）

    Date d = null;                           // 声明 Date 类型成员变量 d，初始化为 null，用于存储反序列化恢复的日期对象

    /**
     * 构造函数：从文件中反序列化恢复 Date 对象
     */
    UnSerializeDate() {                      // 默认构造方法（无参）
        try {                                // try 块开始，捕获可能抛出的 IOException 或 ClassNotFoundException
            FileInputStream f = new FileInputStream("src\\chp7_io\\exp7_9\\date.ser");  // 创建 FileInputStream 读取序列化文件
            ObjectInputStream s = new ObjectInputStream(f);       // 创建 ObjectInputStream，包装 FileInputStream，用于读取对象
            d = (Date) s.readObject();       // readObject() 从流中反序列化一个对象，强制转换为 Date 类型并赋值给 d
            f.close();                       // 关闭 FileInputStream，释放文件资源
        } catch (Exception e) {              // 捕获所有异常（IOException、ClassNotFoundException 等）
            e.printStackTrace();             // 打印异常的堆栈跟踪信息，便于调试和错误定位
        }                                    // catch 块结束

    }                                        // 构造函数结束

    public static void main(String args[]) { // 程序入口 main 方法
        UnSerializeDate a = new UnSerializeDate();  // 创建 UnSerializeDate 对象，触发构造函数：从文件中反序列化 Date
        System.out.println("The date read is :" + a.d.toString());  // 输出反序列化恢复的日期对象
    }                                        // main 方法结束

}                                            // UnSerializeDate 类结束
