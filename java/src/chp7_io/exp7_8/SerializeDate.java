/**
 * 【功能说明】
 *   演示 Java 对象序列化 (Serialization) 机制。程序创建一个 Date 对象（当前时间），
 *   通过 ObjectOutputStream 将其序列化（转换为字节流）并写入到文件 date.ser 中。
 *   序列化可以将 Java 对象的状态（成员变量值）保存到持久化存储介质中。
 *   配套程序 UnSerializeDate（exp7_9）负责从文件中反序列化恢复此对象。
 *
 * 【知识点】
 *   1. 对象序列化 (Serialization)：将 Java 对象的状态转换为字节序列，以便存储或网络传输。
 *   2. Serializable 接口：标记接口（无方法），实现它的类才具备序列化能力。Date 类已默认实现。
 *   3. ObjectOutputStream：对象输出流，通过 writeObject() 将对象写入底层的字节输出流。
 *   4. writeObject(Object obj)：将指定对象序列化为字节流写入输出目标。
 *   5. FileOutputStream：底层字节输出流，将序列化后的字节写入到磁盘文件。
 *   6. 文件扩展名 .ser：通常约定使用 .ser 扩展名表示序列化文件（Serialization）。
 *   7. transient 关键字：如果类的某些字段不希望被序列化，可以标记为 transient。
 *   8. serialVersionUID：序列化版本号，用于确保序列化和反序列化使用兼容的类版本。
 */
package chp7_io.exp7_8;                      // 声明包路径，位于 chp7_io 实验包下的 exp7_8 子包中

import java.io.FileOutputStream;             // 导入 FileOutputStream 类，文件字节输出流，用于向文件写入字节数据
import java.io.IOException;                  // 导入 IOException 类，处理输入/输出操作异常
import java.io.ObjectOutputStream;           // 导入 ObjectOutputStream 类，对象输出流，可将 Java 对象序列化后写入输出流
import java.util.Date;                       // 导入 Date 类，用于创建当前日期时间对象（该类已实现 Serializable 接口）

public class SerializeDate {                 // 定义 SerializeDate 公有类（序列化日期演示类）

    Date d;                                  // 声明 Date 类型成员变量 d，存储要序列化的日期对象

    /**
     * 构造函数：创建一个 Date 对象，并将其序列化到文件中
     */
    SerializeDate() {                        // 默认构造方法（无参）
        d = new Date();                      // 创建 Date 对象，获取当前日期时间（自动初始化为当前系统时间）

        try {                                // try 块开始，捕获可能抛出的 IOException
            FileOutputStream f = new FileOutputStream("date.ser");  // 创建 FileOutputStream，指向序列化输出文件 date.ser
            ObjectOutputStream s = new ObjectOutputStream(f);       // 创建 ObjectOutputStream，包装 FileOutputStream，用于写入对象
            s.writeObject(d);                // 将 Date 对象 d 序列化并写入文件（自动调用 Date 的序列化逻辑）
            f.close();                       // 关闭 FileOutputStream，释放文件资源（注意：应先关闭 ObjectOutputStream）
        } catch (IOException e) {            // 捕获序列化过程中可能发生的 IO 异常
            e.printStackTrace();             // 打印异常的堆栈跟踪信息，帮助定位错误发生的位置
        }                                    // catch 块结束

    }                                        // 构造函数结束

    public static void main(String args[]) { // 程序入口 main 方法
        SerializeDate b = new SerializeDate();  // 创建 SerializeDate 对象，触发构造函数：创建 Date 并序列化到文件
        System.out.println("The saved date is :" + b.d.toString());  // 输出已保存的日期对象（通过 toString() 转换为可读字符串）
    }                                        // main 方法结束

}                                            // SerializeDate 类结束
