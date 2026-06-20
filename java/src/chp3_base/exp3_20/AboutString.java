/**
 * 【功能说明】
 * 本程序演示了 Java 中 String 对象的创建方式及引用比较（==）的特性。
 * 程序通过不同方式创建了多个内容相同的字符串，然后使用 == 运算符
 * 比较它们的引用是否相等，展示了字符串常量池（String Pool）
 * 的自动优化机制——编译期确定的字符串字面量会被合并到常量池中，
 * 而通过 new 创建的字符串对象则在堆上分配新内存。
 *
 * 【知识点】
 * 1. String 是不可变对象（Immutable），一旦创建内容不可更改。
 * 2. 字符串常量池（String Pool / String Intern Cache）：
 *    Java 虚拟机将编译期确定的字符串字面量放入常量池，
 *    相同内容的常量字符串引用会被复用。
 * 3. == 与 equals() 的区别：
 *    - == 比较的是对象的引用（内存地址）是否相同
 *    - equals() 比较的是字符串的内容是否相同
 * 4. 字符串连接优化：编译期可以确定的字符串连接（如 "A" + "B"）
 *    会被编译器优化为常量 "AB"，存入常量池。
 * 5. new String("...") 会在堆上创建新的 String 对象，
 *    不会复用到常量池中的已有对象。
 * 6. 运行期确定的连接（如字符串变量的 +）不会在编译期优化。
 * 7. 本程序中的比较结果：
 *    - b 使用变量 a 连接，运行期确定，不进入常量池
 *    - c 和 d 是编译期常量连接，进入常量池且指向同一对象
 *    - e 是 new 创建的新对象，堆上新地址
 */
package chp3_base.exp3_20;                              // 包声明，该文件位于 chp3_base.exp3_20 包中

public class AboutString {                              // 声明一个公共类 AboutString
    public static void main(String[] args) {             // 主方法，程序执行的入口
        String a = "HUST",                              // 定义字符串常量 "HUST"，放入 String Pool
                b = a + ".AIA.Java";                    // 变量 a + 常量：运行期确定连接，在堆上创建新字符串
        String c = "HUST" + ".AIA.Java",                // 编译期常量连接，优化为 "HUST.AIA.Java" 放入常量池
                d = "HUST.AIA" + ".Java";               // 同样编译期优化为 "HUST.AIA.Java"，与 c 指向同一常量池对象
        String e = new String("HUST.AIA.Java");         // 使用 new 关键字在堆上创建新对象（内容相同但引用不同）
        if (b == c) {                                   // b 是运行期拼接（堆上新对象），c 是常量池对象，引用不同
            System.out.println("长江悲已滞，万里念将归。");      // 该语句不会执行（b != c）
        }                                               // if 代码块结束
        if (c == d) {                                   // c 和 d 都是编译期常量，指向常量池中同一个对象，引用相同
            System.out.println("为中华之崛起而读书。");         // 该语句会执行（c == d）
        }                                               // if 代码块结束
        if (d == e) {                                   // d 是常量池对象，e 是 new 创建的堆对象，引用不同
            System.out.println("自古谁无死，留取丹心照汗青。");   // 该语句不会执行（d != e）
        }                                               // if 代码块结束
        System.out.println("人民只有人民，才是创造历史的动力。");// 无条件执行：直接输出一句话
    }                                                   // 主方法结束
}                                                       // 类定义结束
