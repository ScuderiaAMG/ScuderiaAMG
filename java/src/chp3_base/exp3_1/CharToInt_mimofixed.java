/**
 * 【功能说明】
 * 本程序演示 Java 中 char 类型与 int 类型之间的运算与转换。
 * 具体来说，它展示了一个 char 变量（中文字符'好'）与一个 int 变量相加时，
 * char 会被自动提升（promotion）为 int（即取其 Unicode 编码值），然后进行整数加法。
 * 程序还通过 Integer.toHexString() 将 char 的 Unicode 值转换为十六进制字符串，
 * 以及通过 new Integer(charVar).toString() 将 char 的数值以十进制字符串形式输出。
 *
 * 【知识点】
 * 1. 基本数据类型转换：char → int 的自动类型提升（widening primitive conversion）。
 * 2. char 类型在 Java 中占 16 位，存储的是 Unicode 字符编码（0 ~ 65535）。
 * 3. Integer.toHexString() —— 将整数转换为十六进制字符串。
 * 4. Integer 包装类的构造方法 new Integer(charVar) —— 将 char 的数值转为 Integer 对象。
 * 5. 字符串连接运算符（+）在遇到字符串时的拼接行为。
 * 6. 转义字符 \\u 在输出 Unicode 表示形式时的使用。
 */
package chp3_base.exp3_1;                               // 包声明，指明该类位于 chp3_base.exp3_1 包中
public class CharToInt_mimofixed {                                 // 公共类 CharToInt，类名与文件名一致
    public static void main(String[] args) {              // main 方法：Java 程序的入口点
        int intResult, intVar = 10;                      // 声明两个 int 变量：intResult（未初始化），intVar 初始化为 10
        char charVar = '好';                              // 声明 char 类型变量 charVar，赋值为中文字符 '好'
        intResult = intVar + charVar;                    // charVar 自动提升为 int（'好' 的 Unicode 编码值），再与 intVar 相加
        System.out.println("The char is: " + charVar);   // 输出字符本身，字符串拼接 char 变量时显示其字符表示
        System.out.println("The char's Unicode is: \\u"  // 输出 "The char's Unicode is: \u"（注意转义）
                + Integer.toHexString((int)charVar));    // 将 charVar 的 Unicode 编码值转换为十六进制字符串并拼接输出
        System.out.println("The int value corresponding to the char is: "  // 输出提示文字
                + Integer.valueOf(charVar).toString());      // 通过 Integer.valueOf() 将 char 数值转换为十进制字符串输出
        System.out.println("Int " + intVar               // 输出提示文字 "Int "
                + " adds the char, the result is: "      // 拼接中间文字
                + intResult);                            // 拼接最终计算结果并输出
    }                                                    // main 方法结束
}                                                        // 类定义结束
