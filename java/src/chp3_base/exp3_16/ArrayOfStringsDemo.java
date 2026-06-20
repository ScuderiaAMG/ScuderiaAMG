/**
 * 【功能说明】
 * 本程序演示了 Java 中 String 类型数组的声明、初始化及遍历。
 * 程序使用静态初始化方式创建了一个包含 3 个字符串的数组，
 * 然后通过 for 循环遍历每个元素，并调用 toLowerCase() 方法
 * 将每个字符串转换为小写后输出。
 *
 * 【知识点】
 * 1. String 类型数组的声明与静态初始化：
 *    String[] anArray = { "值1", "值2", "值3" };
 *    静态初始化时无需使用 new 关键字，数组长度由初始值个数自动确定。
 * 2. 数组的 length 属性用于获取数组元素个数。
 * 3. String 类的 toLowerCase() 方法：将字符串中的所有字符转换为小写形式。
 *    注意：该方法不会修改原字符串（String 是不可变的），而是返回一个新的字符串。
 * 4. 数组元素类型可以是任意引用类型，String 是引用类型的一种。
 * 5. System.out.println() 方法可以接受字符串参数并输出后换行。
 */
package chp3_base.exp3_16;                              // 包声明，该文件位于 chp3_base.exp3_16 包中
public class ArrayOfStringsDemo {                       // 声明一个公共类 ArrayOfStringsDemo
    public static void main(String[] args) {             // 主方法，程序执行的入口
        String[] anArray = { "String One",              // 声明并静态初始化一个 String 数组
                "String Two",                           // 第二个元素
                "String Three" };                       // 第三个元素，数组长度自动为 3
        for (int i = 0; i < anArray.length; i++) {       // 遍历数组，从索引 0 到 length-1
            System.out.println(anArray[i].toLowerCase());// 获取第 i 个元素，调用 toLowerCase() 转换为小写并输出
        }                                                // for 循环结束
    }                                                    // 主方法结束
}                                                        // 类定义结束
