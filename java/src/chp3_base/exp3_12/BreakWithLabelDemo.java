/**
 * 【功能说明】
 * 本程序演示了 Java 中带标签的 break 语句（Labeled Break）的用法。
 * 程序在一个二维数组中搜索指定的整数值（12），
 * 当找到目标值时，使用带标签的 break 语句直接跳出外层循环，
 * 并输出目标值所在的行索引和列索引。
 *
 * 【知识点】
 * 1. 带标签的 break 语句：break label 可以跳出指定标签所在的循环块，
 *    而不仅仅是当前最内层的循环。
 * 2. 二维数组的定义和遍历：int[][] arrayOfInts = { {...}, {...}, {...} };
 * 3. 嵌套循环（外层循环遍历行，内层循环遍历列）。
 * 4. 布尔标志位的使用：foundIt 用于记录是否找到目标值。
 * 5. for 循环中可以在外部声明循环变量，以便在循环结束后访问其值。
 * 6. 带标签的 break 与普通 break 的区别：
 *    - 普通 break 只能跳出当前最内层的循环
 *    - 带标签的 break 可以跳出任意层级的循环
 */
package chp3_base.exp3_12;                              // 包声明，该文件位于 chp3_base.exp3_12 包中
public class BreakWithLabelDemo {                       // 声明一个公共类 BreakWithLabelDemo
    public static void main(String[] args) {             // 主方法，程序执行的入口
        int[][] arrayOfInts = { { 32, 87, 3, 589 },     // 声明并初始化一个二维 int 数组（3行4列）
                { 12, 1076, 2000, 8 },                  // 第二行包含目标值 12
                { 622, 127, 77, 955 } };                // 第三行的数据
        int searchFor = 12;                             // 定义要搜索的目标值
        int i = 0;                                      // 外层循环的行索引，在循环外部声明以便后续使用
        int j = 0;                                      // 内层循环的列索引，在循环外部声明以便后续使用
        boolean foundIt = false;                        // 布尔标志位，记录是否找到了目标值，初始为 false
        search: for (; i < arrayOfInts.length; i++) {   // 标签 search 标记外层循环；遍历每一行
            for (j = 0; j < arrayOfInts[i].length; j++) {// 内层循环，遍历当前行的每一列
                if (arrayOfInts[i][j] == searchFor) {   // 判断当前元素是否等于目标值
                    foundIt = true;                     // 找到目标值，将标志位置为 true
                    break search;                       // 带标签的 break：跳出 search 标签标记的外层循环
                }                                       // 内层 if 代码块结束
            }                                           // 内层 for 循环结束
        }                                               // 外层 for 循环结束
        if (foundIt) {                                  // 判断是否找到了目标值
            System.out.println("Found " + searchFor     // 输出找到的目标值及其位置（行索引和列索引）
                    + " at " + i + ", " + j);
        } else {                                        // 如果未找到目标值
            System.out.println(searchFor                // 输出未找到的提示信息
                    + "not in the array");
        }                                               // if-else 代码块结束
    }                                                   // 主方法结束
}                                                       // 类定义结束
