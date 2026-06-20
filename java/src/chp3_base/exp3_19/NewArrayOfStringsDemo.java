/**
 * 【功能说明】
 * 本程序与 exp3_16 中的 ArrayOfStringsDemo 功能相同，
 * 但使用了增强型 for 循环（for-each）来遍历 String 数组，
 * 展示了 Java 5 引入的 for-each 语法的简洁性。
 * 程序定义了一个 String 数组，然后遍历每个元素并调用
 * toLowerCase() 方法转换为小写后输出。
 *
 * 【知识点】
 * 1. 增强型 for 循环（for-each）：
 *    for (元素类型 变量名 : 数组或集合) { ... }
 *    用于遍历数组或实现了 Iterable 接口的集合类。
 * 2. for-each 与传统 for 循环的比较：
 *    - for-each 更简洁，无需关心索引
 *    - for-each 无法获取当前元素的索引位置
 *    - for-each 无法在遍历过程中修改数组元素（但可以读取）
 *    - for-each 遍历顺序是固定的（从第一个到最后一个）
 * 3. String 类的 toLowerCase() 方法：返回将原字符串所有字符
 *    转换为小写后的新字符串（原字符串不变，因为 String 不可变）。
 * 4. 数组静态初始化语法与 exp3_16 相同。
 */
package chp3_base.exp3_19;                              // 包声明，该文件位于 chp3_base.exp3_19 包中
public class NewArrayOfStringsDemo {                    // 声明一个公共类 NewArrayOfStringsDemo
    public static void main(String[] args) {             // 主方法，程序执行的入口
        String[] anArray = { "String One",              // 声明并静态初始化一个 String 数组
                "String Two",                           // 第二个元素
                "String Three" };                       // 第三个元素
        for (String s : anArray) {                      // 使用增强型 for 循环遍历数组（每次迭代取出一个元素赋给 s）
            System.out.println(s.toLowerCase());        // 将当前字符串 s 转换为小写并输出（带换行）
        }                                               // for-each 循环结束
    }                                                   // 主方法结束
}                                                       // 类定义结束
