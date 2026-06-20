/**
 * 【功能说明】
 * 本程序通过 Java 基本数据类型的包装类（Byte、Short、Integer、Long、Float、Double）
 * 访问其类常量，分别输出每种类型的最大值（MAX_VALUE）和最小值（MIN_VALUE），
 * 以及浮点类型的正无穷大（POSITIVE_INFINITY）、负无穷大（NEGATIVE_INFINITY）
 * 和非数字（NaN）常量值。
 * 这些常量在 JDK 的包装类中以 public static final 形式定义。
 *
 * 【知识点】
 * 1. 包装类（Wrapper Class）：Byte、Short、Integer、Long、Float、Double。
 * 2. 类常量（static final）：MAX_VALUE、MIN_VALUE、POSITIVE_INFINITY、
 *    NEGATIVE_INFINITY、NaN。
 * 3. 各类基本数据类型的取值范围：
 *    byte:   -128 ~ 127 (8位有符号)
 *    short:  -32768 ~ 32767 (16位有符号)
 *    int:    -2^31 ~ 2^31-1 (32位有符号)
 *    long:   -2^63 ~ 2^63-1 (64位有符号)
 *    float:  ~ ±3.4E38 (32位 IEEE 754)
 *    double: ~ ±1.8E308 (64位 IEEE 754)
 * 4. 浮点数特殊值：Infinity（无穷大）和 NaN（Not a Number）。
 * 5. 字符串连接运算符（+）在拼接不同类型时的自动类型转换。
 */
package chp3_base.exp3_3;                               // 包声明，指明该类位于 chp3_base.exp3_3 包中
public class SomeConstTest {                             // 公共类 SomeConstTest
    public static void main(String[] args) {             // main 方法：Java 程序的入口
        // 输出 byte 类型的最大值和最小值                      // 单行注释：说明以下代码的功能
        System.out.println("Byte.MAX_VALUE = " + Byte.MAX_VALUE);   // 输出 byte 类型的最大值（127）
        System.out.println("Byte.MIN_VALUE = " + Byte.MIN_VALUE + '\n'); // 输出 byte 类型的最小值（-128），并追加换行符
//      System.out.println();                            // 被注释掉的方法调用，用于输出一个空行（此处被字符 '\n' 替代）
        // 输出 short 类型的最大值和最小值
        System.out.println("Short.MAX_VALUE = " + Short.MAX_VALUE); // 输出 short 类型的最大值（32767）
        System.out.println("Short.MIN_VALUE = " + Short.MIN_VALUE + '\n'); // 输出 short 类型的最小值（-32768）
        // 输出 int 类型的最大值和最小值
        System.out.println("Integer.MAX_VALUE = " + Integer.MAX_VALUE); // 输出 int 类型的最大值（2147483647）
        System.out.println("Integer.MIN_VALUE = " + Integer.MIN_VALUE + '\n'); // 输出 int 类型的最小值（-2147483648）
        // 输出 long 类型的最大值和最小值
        System.out.println("Long.MAX_VALUE = " + Long.MAX_VALUE);   // 输出 long 类型的最大值（9223372036854775807L）
        System.out.println("Long.MIN_VALUE = " + Long.MIN_VALUE + '\n'); // 输出 long 类型的最小值（-9223372036854775808L）
        // 输出 float 类型的最大值和最小值
        System.out.println("Float.MAX_VALUE = " + Float.MAX_VALUE); // 输出 float 类型的最大值（约 3.4028235E38）
        System.out.println("Float.MIN_VALUE = " + Float.MIN_VALUE + '\n'); // 输出 float 类型的最小正值（约 1.4E-45）
        // 输出 double 类型的最大值和最小值
        System.out.println("Double.MAX_VALUE = " + Double.MAX_VALUE); // 输出 double 类型的最大值（约 1.7976931348623157E308）
        System.out.println("Double.MIN_VALUE = " + Double.MIN_VALUE + '\n'); // 输出 double 类型的最小正值（约 4.9E-324）
        // 输出 float 类型的正无穷大和负无穷大
        System.out.println("Float.POSITIVE_INFINITY = " + Float.POSITIVE_INFINITY); // 输出 float 正无穷大（实际为 Infinity）
        System.out.println("Float.NEGATIVE_INFINITY = " + Float.NEGATIVE_INFINITY + '\n'); // 输出 float 负无穷大（实际为 -Infinity）
        // 输出 double 类型的正无穷大和负无穷大
        System.out.println("Double.POSITIVE_INFINITY = " + Double.POSITIVE_INFINITY); // 输出 double 正无穷大
        System.out.println("Double.NEGATIVE_INFINITY = " + Double.NEGATIVE_INFINITY + '\n'); // 输出 double 负无穷大
        // 输出 float 类型的 NaN（非数字）                    // 说明：NaN 表示 0/0 等无意义运算的结果
        System.out.println("Float.NaN = " + Float.NaN + '\n');     // 输出 Float.NaN（显示为 NaN）
        // 输出 double 类型的 NaN（非数字）
        System.out.println("Double.NaN = " + Double.NaN + '\n');   // 输出 Double.NaN（显示为 NaN）
    }                                                    // main 方法结束
}                                                        // 类定义结束
