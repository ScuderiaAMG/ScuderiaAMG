/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了Java异常处理机制中的 try-catch-finally 结构。
 * 相较于 exp6_2，本版本在 writeList() 方法中增加了异常处理，
*  使用 try 块包围可能抛出异常的代码，通过 catch 分别捕获
 * IndexOutOfBoundsException（索引越界）和 IOException（I/O错误），
 * 并使用 finally 块确保 PrintWriter 流被正确关闭。
 * 该示例展示了如何通过结构化异常处理使程序在发生错误时
 * 仍能正常执行清理操作并优雅终止。
 *
 * 【知识点】
 * 1. try-catch-finally 异常处理基本结构
 * 2. 多 catch 块：按异常类型分别处理
 *    （子类在前，父类在后）
 * 3. IndexOutOfBoundsException：索引越界异常（RuntimeException子类）
 * 4. IOException：输入输出异常（已检查异常）
 * 5. finally 块：无论是否发生异常都会执行
 *    ——适合资源释放、关闭连接等清理操作
 * 6. System.err 标准错误输出流
 * 7. e.getMessage() 获取异常描述信息
 * 8. 防御性编程：在 finally 中进行 null 检查后再关闭资源
 * ============================================================
 */
package chp6_exception.exp6_3;                             // 声明包路径，属于第6章异常处理实验3
import java.io.FileWriter;                                  // 导入FileWriter类，用于写入字符文件
import java.io.IOException;                                 // 导入IOException类，用于捕获输入输出异常
import java.io.PrintWriter;                                 // 导入PrintWriter类，提供格式化打印功能
import java.util.ArrayList;                                 // 导入ArrayList类，动态数组实现

class ListOfNumbers_mimofixed {                                       // 定义包访问级别的ListOfNumbers类
    private ArrayList<Integer> list;                        // 私有成员变量：存储整数的ArrayList列表
    private static final int size = 10;                     // 私有静态常量：列表大小固定为10

    public ListOfNumbers_mimofixed() {                                // 构造方法：初始化整数列表
        list = new ArrayList<Integer>(size);                // 创建初始容量为10的ArrayList实例
        for (int i = 0; i < size; i++)                      // for循环，从0到9共10次迭代
            list.add(Integer.valueOf(i));                       // 将Integer对象（值i）添加到列表中，使用valueOf替代废弃的构造函数
    }                                                       // 构造方法结束

    public void writeList() {                               // writeList方法：将列表内容写入文件
        PrintWriter out = null;                             // 声明PrintWriter引用并初始化为null（finally中需要判断）
        try {                                               // try块开始：监视可能抛出异常的代码
            System.out.println("Entering try statement");   // 打印提示信息，表示进入try块
            out = new PrintWriter(new FileWriter("OutFile.txt")); // 创建PrintWriter写入OutFile.txt（可能抛出IOException）
            for (int i = 0; i < size; i++) {                // for循环遍历列表
                out.println("Value at: " + i + " = " + list.get(i)); // 写入索引i和对应的值（list.get(i)可能抛出IndexOutOfBoundsException）
            }                                               // for循环结束
        } catch (IndexOutOfBoundsException e) {             // 捕获索引越界异常（RuntimeException子类）
            System.err.println("Caught IndexOutOfBoundsException: " + // 在标准错误流打印异常信息
                    e.getMessage());                        // 调用异常对象的getMessage()获取详细描述
        } catch (IOException e) {                           // 捕获I/O异常（已检查异常）
            System.err.println("Caught IOException: " + e.getMessage()); // 在标准错误流打印I/O异常信息
        } finally {                                         // finally块：无论是否发生异常都会执行
            if (out != null) {                              // 判断PrintWriter是否已成功创建（防止NullPointerException）
                System.out.println("Closing PrintWriter");  // 打印提示信息，表示正在关闭输出流
                out.close();                                // 关闭PrintWriter，释放系统资源
            } else {                                        // 如果PrintWriter为null（创建时发生异常）
                System.out.println("PrintWriter not open"); // 打印提示信息，表示输出流未成功打开
            }                                               // if-else结束
        }                                                   // finally块结束
    }                                                       // writeList方法结束
}                                                           // ListOfNumbers类结束

public class TestListOfNumbers_mimofixed {                            // 公开测试类TestListOfNumbers
    public static void main(String[] args) {                // 程序入口点
        ListOfNumbers_mimofixed list = new ListOfNumbers_mimofixed();           // 创建ListOfNumbers实例，初始化包含0-9的整数列表
        list.writeList();                                   // 调用writeList方法，该方法内部包含完善的异常处理
    }                                                       // main方法结束
}                                                           // 类定义结束
