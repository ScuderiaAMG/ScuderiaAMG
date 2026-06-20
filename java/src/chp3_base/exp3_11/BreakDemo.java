/**
 * 【功能说明】
 * 本程序演示 break 语句在循环中的用法。
 * 程序在一个整数数组中查找目标值（searchFor = 12），
 * 使用 for 循环依次遍历数组元素，当找到目标值时，
 * 设置 foundIt 标志为 true 并使用 break 语句立即退出循环。
 * 最后根据 foundIt 标志输出查找结果（找到则输出位置索引，否则提示未找到）。
 *
 * 【知识点】
 * 1. break 语句：在循环中用于立即终止当前循环，程序继续执行循环后的第一条语句。
 * 2. for 循环的省略形式：for (; i < arrayOfInts.length; i++) 省略了初始化部分，
 *    i 已在循环外声明和初始化。
 * 3. 循环外访问循环变量：i 声明在循环外，循环结束后仍可访问其值，
 *    用于记录找到目标时的下标位置。
 * 4. 搜索算法（线性查找）：从数组第一个元素开始逐个比较，找到则返回。
 * 5. boolean 标志变量（foundIt）：用于记录是否找到目标，避免在循环结束后重复判断。
 */
package chp3_base.exp3_11;                               // 包声明，该类位于 chp3_base.exp3_11 包中
public class BreakDemo {                                 // 公共类 BreakDemo
    public static void main(String[] args) {             // main 方法：程序入口
        int[] arrayOfInts = { 32, 87, 3, 589, 12, 1076, 2000, 8, 622, 127 }; // 声明并初始化 int 数组（10 个元素）
        int searchFor = 12;              // 声明 int 变量 searchFor 并赋值为 12（待查找的目标值）
        int i = 0;                       // 声明循环变量 i 并初始化为 0（声明在循环外，以便循环后使用）
        boolean foundIt = false;         // 声明 boolean 标志变量 foundIt 并初始化为 false（表示尚未找到）
        for (; i < arrayOfInts.length; i++) {   // for 循环：省略初始化部分（i 已在外初始化），遍历数组
            if (arrayOfInts[i] == searchFor) {   // 判断当前数组元素是否等于目标值 12
                foundIt = true;          // 找到目标，将标志设为 true
                break;                   // break：立即终止循环，不再继续遍历
            }                            // if 语句结束
        }                                // for 循环结束
        if (foundIt) {                   // 如果 foundIt 为 true（表示已找到）
            System.out.println("Found " + searchFor + " at index " + i); // 输出找到的目标值及其索引位置
        } else {                         // 否则（未找到）
            System.out.println(searchFor + " not in the array"); // 输出未找到提示信息
        }                                // if-else 结束
    }                                                    // main 方法结束
}                                                        // 类定义结束
