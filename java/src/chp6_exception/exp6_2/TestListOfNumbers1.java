/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了使用 FileWriter 和 PrintWriter 进行文件输出操作。
 * 程序创建一个 ListOfNumbers 类，内部维护一个 ArrayList 整数列表，
 * 并提供了将列表内容写入文件 "OutFile.txt" 的方法 writeList()。
 * ⚠ 注意：writeList() 方法未处理 FileWriter 构造时可能抛出的
 * IOException（已检查异常），也未在方法签名中使用 throws 声明，
 * 因此该代码在编译时将报 "未报告的异常错误"。
 * 此示例旨在说明已检查异常（Checked Exception）必须被处理
 * 或声明的编译时规则。
 *
 * 【知识点】
 * 1. java.io.FileWriter：字符流写入文件的便捷类
 * 2. java.io.PrintWriter：带格式的字符输出流
 * 3. java.util.ArrayList：动态数组（泛型集合）
 * 4. Integer 包装类与自动装箱
 * 5. 已检查异常（Checked Exception）——IOException
 * 6. 编译时异常处理规则：必须 catch 或 throws
 * 7. 异常处理的两种方式：try-catch 包围 或 方法签名 throws 声明
 * ============================================================
 */
package chp6_exception.exp6_2;                             // 声明包路径，属于第6章异常处理实验2

import java.io.FileWriter;                                  // 导入FileWriter类，用于写入字符文件
import java.io.PrintWriter;                                 // 导入PrintWriter类，提供格式化打印功能
import java.util.ArrayList;                                 // 导入ArrayList类，动态数组实现

class ListOfNumbers {                                       // 定义包访问级别的ListOfNumbers类
    private ArrayList<Integer> list;                        // 私有成员变量：存储整数的ArrayList列表
    private static final int size = 10;                     // 私有静态常量：列表大小固定为10

    public ListOfNumbers() {                                // 构造方法：初始化整数列表
        list = new ArrayList<Integer>(size);                 // 创建初始容量为10的ArrayList实例
        for (int i = 0; i < size; i++)                      // for循环，从0到9共10次迭代
            list.add(new Integer(i));                       // 将Integer对象（值i）添加到列表中
    }                                                       // 构造方法结束

    // 将list中的整数写入OutFile.txt文件
    public void writeList() {                               // writeList方法：将列表内容写入文件
        PrintWriter out = new PrintWriter(                  // 创建PrintWriter对象 --- 此行可能抛出IOException！
                new FileWriter("OutFile.txt"));             // 创建FileWriter以追加方式写入OutFile.txt文件

        for (int i = 0; i < size; i++)                      // for循环遍历列表
            out.println("Value at: " + i + " = " + list.get(i)); // 将索引i和对应的值写入文件

        out.close();                                        // 关闭输出流，释放系统资源
    }                                                       // writeList方法结束
}                                                           // ListOfNumbers类结束

public class TestListOfNumbers1 {                           // 公开测试类TestListOfNumbers1
    public static void main(String[] args) {                // 程序入口点
        ListOfNumbers list = new ListOfNumbers();           // 创建ListOfNumbers实例，初始化包含0-9的整数列表
        list.writeList();                                   // 调用writeList方法将列表写入文件（此调用可能引发编译错误）
    }                                                       // main方法结束
}                                                           // 类定义结束
