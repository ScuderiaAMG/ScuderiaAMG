/**
 * 【功能说明】
 * 本程序演示了 Java 中 System.arraycopy() 方法的用法。
 * 程序将一个 char 数组从指定位置开始的部分元素复制到另一个数组中，
 * 然后将复制后的 char 数组转为字符串并输出。
 * 源数组包含 "decaffeinated" 的字符序列，
 * 从索引 2（即 'c'）开始复制连续 7 个字符到目标数组，
 * 最终输出结果为 "caffein"。
 *
 * 【知识点】
 * 1. System.arraycopy(Object src, int srcPos, Object dest, int destPos, int length)
 *    这是 Java 提供的底层数组复制方法，使用 native 实现，效率较高。
 *    参数说明：
 *    - src：源数组
 *    - srcPos：源数组中的起始位置（索引）
 *    - dest：目标数组
 *    - destPos：目标数组中的起始位置（索引）
 *    - length：要复制的元素个数
 * 2. char 数组与 String 的转换：
 *    new String(char[] value) 可以使用 char 数组构造一个 String 对象。
 * 3. 数组长度是固定的，因此在复制前需确保目标数组容量足够。
 * 4. arraycopy 是浅复制（Shallow Copy）：对于引用类型数组，
 *    复制的是引用而非对象本身（但对于 char 等基本类型没有区别）。
 * 5. 如果源数组或目标数组为 null，或者参数越界，
 *    会抛出 NullPointerException 或 ArrayIndexOutOfBoundsException。
 */
package chp3_base.exp3_20;                              // 包声明，该文件位于 chp3_base.exp3_20 包中
public class ArrayCopyDemo {                            // 声明一个公共类 ArrayCopyDemo
    public static void main(String[] args) {             // 主方法，程序执行的入口
        char[] copyFrom =                               // 声明并初始化源 char 数组（包含 "decaffeinated" 的全部字符）
                {'d','e','c','a','f','f','e','i','n','a','t','e','d'};
        char[] copyTo = new char[7];                    // 创建目标数组，长度为 7（刚好容纳 7 个字符）
        System.arraycopy(copyFrom, 2, copyTo, 0, 7);    // 从 copyFrom 的索引 2 开始复制 7 个字符到 copyTo 的索引 0 开始处
        System.out.println(new String(copyTo));         // 将 char 数组转换为 String 并输出（输出结果为 "caffein"）
    }                                                   // 主方法结束
}                                                       // 类定义结束
