/**
 * 【功能说明】
 * 本程序演示了 Java 中不规则二维数组（Jagged Array）的静态初始化与遍历。
 * 程序定义了一个 String 类型的二维数组 cartoons，每个子数组（每行）
 * 代表一个卡通系列及其角色列表，各行的长度不同（不规则数组）。
 * 程序遍历该二维数组，输出每行的索引、元素个数以及所有元素内容，
 * 并使用三元运算符在元素之间添加逗号分隔符。
 *
 * 【知识点】
 * 1. 不规则数组（Jagged Array）：二维数组中每行的列数可以不同。
 *    Java 中二维数组本质上是"数组的数组"，每个子数组可以有独立的长度。
 * 2. 二维数组的静态初始化：
 *    String[][] arr = { {"a","b"}, {"c","d","e"} };
 *    每行是一个独立的 String 数组字面量。
 * 3. 嵌套 for 循环遍历不规则数组：外层循环行，内层循环列，
 *    每行的列数由 cartoons[i].length 动态获取。
 * 4. 三元运算符在输出格式控制中的应用：
 *    (j < cartoons[i].length - 1 ? ", " : "")
 *    如果不是最后一个元素，则添加逗号和空格，否则添加空字符串。
 * 5. System.out.print() 按行输出，System.out.println() 换行。
 */
package chp3_base.exp3_18;                              // 包声明，该文件位于 chp3_base.exp3_18 包中
public class ArrayOfArraysDemo2 {                       // 声明一个公共类 ArrayOfArraysDemo2
    public static void main(String[] args) {             // 主方法，程序执行的入口
        String[][] cartoons = {                         // 声明并静态初始化一个 String 类型的二维数组（不规则数组）
                { "Flintstones", "Fred", "Wilma",       // 第一行：卡通系列名 + 角色列表（5 个元素）
                        "Pebbles", "Dino" },
                { "Rubbles", "Barney", "Betty",         // 第二行：4 个元素
                        "Bam Bam" },
                { "Jetsons", "George", "Jane",          // 第三行：7 个元素
                        "Elroy", "Judy", "Rosie","Astro" },
                { "Scooby Doo Gang", "Scooby Doo",      // 第四行：6 个元素
                        "Shaggy", "Velma", "Fred","Daphne" } };
        for (int i = 0; i < cartoons.length; i++) {      // 外层循环：遍历二维数组的每一行
            System.out.print("cartoons[" + i + "]" +    // 输出当前行的索引和元素个数
                    ", " + cartoons[i].length
                    + " elements: ");
            for (int j = 0; j < cartoons[i].length; j++) {// 内层循环：遍历当前行的每一列
                System.out.print(cartoons[i][j]         // 输出当前元素
                        + (j < cartoons[i].length - 1   // 使用三元运算符判断是否为该行最后一个元素
                        ? ", " : ""));                  // 不是最后一个则加逗号空格，是最后一个则不加
            }                                           // 内层 for 循环结束
            System.out.println();                       // 每行输出完毕后换行
        }                                               // 外层 for 循环结束
    }                                                   // 主方法结束
}                                                       // 类定义结束
