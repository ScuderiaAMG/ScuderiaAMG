/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了使用 throws 关键字在方法签名中声明异常，
 * 将异常处理的责任转移给调用者。
 * ListOfNumbersDeclared 类的 writeList() 方法使用 FileWriter
 * 和 PrintWriter 进行文件输出，但不在方法内部处理异常，
 * 而是通过 throws IOException, ArrayIndexOutOfBoundsException
 * 将异常向上抛出。调用方（TestOfDeclared.main）使用
 * try-catch 捕获 Exception（所有异常的父类）进行处理。
 * 此外，该示例使用 Vector 替代 ArrayList，展示了早期集合类。
 *
 * 【知识点】
 * 1. throws 关键字：在方法签名中声明可能抛出的异常
 * 2. 异常传播机制：将异常处理责任转移给调用者
 * 3. 多异常声明：throws 后可跟多个异常类型，用逗号分隔
 * 4. 已检查异常（IOException）必须声明或捕获的编译规则
 * 5. 异常多态：catch(Exception e) 可捕获所有异常类型
 * 6. Vector 类：早期线程安全的动态数组实现
 * 7. System.err 标准错误输出与异常信息格式化
 * ============================================================
 */
package chp6_exception.exp6_5;                             // 声明包路径，属于第6章异常处理实验5

import java.io.FileWriter;                                  // 导入FileWriter类，用于写入字符文件
import java.io.IOException;                                 // 导入IOException类，用于声明/捕获输入输出异常
import java.io.PrintWriter;                                 // 导入PrintWriter类，提供格式化打印功能
import java.util.Vector;                                    // 导入Vector类（线程安全的动态数组，ArrayList的前身）

class ListOfNumbersDeclared_mimofixed {                               // 定义包访问级别的ListOfNumbersDeclared类
    private Vector<Integer> victor;                         // 私有成员变量：存储整数的Vector列表（线程安全）
    private static final int size = 10;                     // 私有静态常量：列表大小固定为10

    public ListOfNumbersDeclared_mimofixed() {                        // 构造方法：初始化整数列表
        victor = new Vector<Integer>(size);                 // 创建初始容量为10的Vector实例
        for (int i = 0; i < size; i++)                      // for循环，从0到9共10次迭代
            victor.addElement(Integer.valueOf(i));              // 使用 addElement 方法添加元素（Vector的旧式API），使用valueOf替代废弃的构造函数
    }                                                       // 构造方法结束

    // 声明异常，将处理责任转交给调用者
    public void writeList() throws IOException,             // 方法声明：抛出IOException（FileWriter/PrintWriter可能抛出）
            ArrayIndexOutOfBoundsException {                // 抛出ArrayIndexOutOfBoundsException（Vector访问可能抛出）
        PrintWriter out = new PrintWriter(                  // 创建PrintWriter对象（可能抛出IOException）
                new FileWriter("OutFile.txt"));             // 创建FileWriter写入OutFile.txt文件

        for (int i = 0; i < size; i++)                      // for循环遍历列表
            out.println("Value at: " + i + " = " + victor.elementAt(i)); // 使用elementAt()方法获取元素并写入文件

        out.close();                                        // 关闭输出流，释放系统资源
    }                                                       // writeList方法结束
}                                                           // ListOfNumbersDeclared类结束

public class TestOfDeclared_mimofixed {                               // 公开测试类TestOfDeclared
    public static void main(String[] args) {                // 程序入口点
        try {                                               // try块开始：调用可能抛出异常的方法
            ListOfNumbersDeclared_mimofixed list = new ListOfNumbersDeclared_mimofixed(); // 创建ListOfNumbersDeclared实例
            list.writeList();                               // 调用writeList方法（该方法声明抛出IOException和ArrayIndexOutOfBoundsException）
        } catch (Exception e) {                             // 捕获所有Exception类型（多态：IOException和ArrayIndexOutOfBoundsException都是Exception子类）
            System.err.println("Caught Exception: " + e.getMessage() + "\n"); // 在标准错误流打印异常信息和换行符
        }                                                   // catch块结束
        System.out.println("A list of numbers is created and stored in OutFile.txt"); // 打印提示信息，表示列表已成功创建并写入文件
    }                                                       // main方法结束
}                                                           // 类定义结束
