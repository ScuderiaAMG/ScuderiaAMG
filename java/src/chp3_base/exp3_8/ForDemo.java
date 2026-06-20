/**
 * 【功能说明】
 * 本程序演示 for 循环的基本用法。
 * 程序定义了一个 int 类型数组，包含 10 个整数元素。
 * 使用标准的 for 循环遍历数组，通过数组下标依次访问每个元素，
 * 并以空格分隔的方式将所有元素输出到一行，最后换行。
 *
 * 【知识点】
 * 1. for 循环语法：for (初始化; 条件判断; 循环后操作) { 循环体 }
 *    - 初始化：int i = 0，在循环开始前执行一次。
 *    - 条件判断：i < arrayOfInts.length，每次循环前检查。
 *    - 循环后操作：i++，每次循环体执行完后执行。
 * 2. 数组的声明与初始化：int[] arrayOfInts = { 值1, 值2, ... }。
 * 3. 数组长度属性：arrayOfInts.length，返回数组中元素的数量。
 * 4. System.out.print()：输出但不换行。
 * 5. System.out.println()：输出空行（换行）。
 */
package chp3_base.exp3_8;                               // 包声明，该类位于 chp3_base.exp3_8 包中
public class ForDemo {                                   // 公共类 ForDemo
    public static void main(String[] args) {             // main 方法：程序入口
        int[] arrayOfInts = { 32, 87, 3, 589, 12, 1076, 2000, 8, 622, 127 }; // 声明并初始化一个 int 数组（10 个元素）
        for (int i = 0; i < arrayOfInts.length; i++) {   // for 循环：i 从 0 开始，循环到数组长度-1，每次 i 自增 1
            System.out.print(arrayOfInts[i] + " ");      // 输出当前下标 i 对应的数组元素，后跟一个空格（不换行）
        }                                                  // for 循环体结束
        System.out.println();                              // 输出一个空行（换行），使光标移到下一行
    }                                                      // main 方法结束
}                                                          // 类定义结束
