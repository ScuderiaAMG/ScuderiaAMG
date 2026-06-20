/**
 * ============================================================
 * 【功能说明】
 * 这是 Java 语言的入门程序，也是学习任何编程语言时的第一个示例。
 * 程序的功能非常简单：在控制台（命令行终端）输出一行文本 "Hello World!"。
 * 它演示了 Java 程序最基本的骨架结构，是所有 Java 程序的起点。
 * ============================================================
 * 【知识点】
 * 1. package 声明 —— Java 中用于组织类的命名空间机制。
 * 2. 类定义 (class) —— Java 是纯面向对象语言，所有代码必须位于类中。
 * 3. main 方法 —— Java 程序的入口点（Entry Point），JVM 从这里开始执行。
 * 4. 方法签名 public static void main(String[] args) 的含义：
 *    - public: 访问修饰符，表示 JVM 可以从外部调用此方法
 *    - static: 静态方法，无需创建对象即可调用
 *    - void: 无返回值
 *    - String[] args: 命令行参数数组
 * 5. System.out.println —— 标准输出流，向控制台打印文本并换行。
 * ============================================================
 */

// 声明包名为 chp1_intro，表示当前类属于 chp1_intro 包
// 包（package）是 Java 中用于组织类和接口的机制，类似于文件系统中的文件夹
// 包名通常使用小写字母，采用反向域名命名规范（如 com.company.project）
package chp1_intro;

// 定义一个名为 HelloWorld 的公共类
// public 关键字表示这是一个公共类，可以被任何其他类访问
// class 是 Java 中定义类的关键字
// 类名 HelloWorld 采用驼峰命名法（PascalCase），首字母大写
// 类名必须与文件名一致（HelloWorld.java）
public class HelloWorld {

    // main 方法是 Java 程序的入口点（entry point）
    // 当程序启动时，Java 虚拟机（JVM）会自动寻找并调用此方法
    // public: 访问修饰符，表示该方法可以被 JVM 从外部访问
    // static: 静态方法，属于类而非类的实例，JVM 无需创建对象即可调用
    // void: 返回值类型，表示该方法不返回任何值
    // main: 方法名，固定的特殊名称，JVM 约定使用此名称作为入口
    // String[] args: 参数，String 类型的数组，用于接收命令行传入的参数
    public static void main(String[] args) {

        // System.out.println 是 Java 的标准输出语句
        // System: java.lang 包中的 final 类，提供系统相关的功能
        // out: System 类中的静态字段，类型为 PrintStream，代表标准输出流（控制台）
        // println: PrintStream 类的方法，打印指定内容并在末尾添加换行符（\n）
        // 双引号 "Hello World!" 是一个字符串字面量（String literal）
        // 分号 ; 表示 Java 语句的结束，每条语句都必须以分号结尾
        System.out.println("Hello World!");

    // 右花括号 } 表示 main 方法的结束
    // 方法体中的所有代码都必须包裹在一对花括号 {} 中
    }

// 右花括号 } 表示 HelloWorld 类的结束
// 类体中的所有成员（字段、方法、构造器等）都必须包裹在类的一对花括号 {} 中
}
