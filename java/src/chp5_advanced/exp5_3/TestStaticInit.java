/**
 * 【功能说明】
 * 本程序演示了Java中静态初始化块（static initializer / static block）的用法。
 * StaticInitDemo类中包含一个静态变量i和一个静态初始化块。
 * 静态初始化块在类加载时自动执行，且仅执行一次，早于任何对象的创建，
 * 也早于main方法的执行。程序输出结果将先显示静态块中的内容，再显示main方法中的内容。
 *
 * 【知识点】
 * 1. 静态初始化块：使用static { ... }语法，在类加载时执行，仅执行一次
 * 2. 静态初始化块的执行时机：类加载阶段，早于main方法的执行
 * 3. 静态初始化块通常用于初始化静态变量或执行类级别的初始化操作
 * 4. 类加载的触发条件：首次访问该类中的静态成员时（包括静态变量、静态方法）
 * 5. Java程序执行顺序：静态初始化块 -> main方法 -> 实例初始化块 -> 构造方法
 * 6. 后缀自增运算符 i++：先使用i的当前值，再使i自增1
 */
package chp5_advanced.exp5_3;                              // 声明包路径，该文件位于chp5_advanced.exp5_3包中

class StaticInitDemo {                                     // 定义StaticInitDemo类，用于演示静态初始化块
    static int i;                                          // 静态变量i，未显式初始化，默认值为0

    static {                                               // 静态初始化块：在类加载时自动执行，仅执行一次
        i = 5;                                             // 将静态变量i赋值为5
        System.out.println("Static code: i=" + i++);       // 输出i的当前值（5），然后i自增为6（后缀自增）
    }
}

public class TestStaticInit {                              // 主类（public），包含程序入口main方法
    public static void main(String args[]) {               // 主方法：程序执行的入口点
        System.out.println(" Main code: i=" + StaticInitDemo.i); // 访问StaticInitDemo的静态变量i，触发类加载，输出i的值（6）
    }
}
