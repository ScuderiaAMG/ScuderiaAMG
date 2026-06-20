/**
 * 【功能说明】
 * 本程序演示了 Java 中二维数组（数组的数组）的创建与遍历。
 * 程序首先创建一个包含 4 行的二维数组（每行是一个一维 int 数组），
 * 然后为每一行动态分配 5 个元素的列空间，
 * 接着为每个元素赋值为其行索引与列索引之和 (i + j)，
 * 最后以矩阵形式打印出所有元素的值。
 *
 * 【知识点】
 * 1. 二维数组的声明：int[][] aMatrix — 本质上是"数组的数组"。
 * 2. 二维数组的创建方式：先创建行，再逐行创建列。
 *    int[][] aMatrix = new int[4][];  // 只指定行数，列数暂不指定
 *    aMatrix[i] = new int[5];         // 逐行为每行分配列空间
 * 3. 数组的 length 属性在不同层级的意义：
 *    - aMatrix.length：二维数组的行数
 *    - aMatrix[i].length：第 i 行的列数
 * 4. 这种逐行分配的方式允许创建"不规则数组（Jagged Array）"，
 *    即每行的列数可以不同（尽管本例中每行都是 5 列）。
 * 5. 嵌套 for 循环遍历二维数组：外层循环遍历行，内层循环遍历列。
 * 6. 二维数组的默认初始值：当只分配行后，每行引用初始为 null。
 *    需要逐行 new int[5] 后才能访问该行的列元素。
 */
package chp3_base.exp3_17;                              // 包声明，该文件位于 chp3_base.exp3_17 包中
public class ArrayOfArraysDemo1 {                       // 声明一个公共类 ArrayOfArraysDemo1
    public static void main(String[] args) {             // 主方法，程序执行的入口
        int[][] aMatrix = new int[4][];                  // 创建一个二维数组，包含 4 行，但每行的列数未指定（初始为 null）
        // 为每个 int 数组（每一行）分配列空间，并为每个元素赋值
        for (int i = 0; i < aMatrix.length; i++) {       // 遍历每一行（i 为行索引）
            aMatrix[i] = new int[5];                     // 为第 i 行分配一个包含 5 个 int 元素的一维数组
            for (int j = 0; j < aMatrix[i].length; j++) {// 遍历当前行的每一列（j 为列索引）
                aMatrix[i][j] = i + j;                   // 将行索引 i 与列索引 j 的和赋给当前元素
            }                                            // 内层 for 循环结束
        }                                                // 外层 for 循环结束
        // 以矩阵形式遍历并打印数组内容
        for (int i = 0; i < aMatrix.length; i++) {       // 遍历每一行
            for (int j = 0; j < aMatrix[i].length; j++) {// 遍历当前行的每一列
                System.out.print(aMatrix[i][j] + " ");   // 打印当前元素并在后面加空格（不换行）
            }                                            // 内层 for 循环结束
            System.out.println();                        // 每打印完一行后换行
        }                                                // 外层 for 循环结束
    }                                                    // 主方法结束
}                                                        // 类定义结束
