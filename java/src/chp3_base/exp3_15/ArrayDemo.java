/**
 * 【功能说明】
 * 本程序演示了 Java 中一维数组的基本用法。
 * 程序首先声明一个 int 类型的数组引用，然后为其分配 10 个元素的空间，
 * 接着使用 for 循环为每个元素赋值（值等于其索引），
 * 最后遍历数组并打印所有元素的值。
 *
 * 【知识点】
 * 1. 数组的声明：int[] anArray;  — 声明一个数组类型的引用变量。
 * 2. 数组的创建：anArray = new int[10];  — 分配内存空间，指定数组长度。
 * 3. 数组的声明和创建也可以合并为一步：int[] anArray = new int[10];
 * 4. 数组的 length 属性：anArray.length 获取数组的长度（元素个数）。
 * 5. 数组元素的访问：通过索引访问，索引从 0 开始，例如 anArray[0]。
 * 6. int 类型的数组元素在创建时会被自动初始化为默认值 0。
 * 7. for 循环遍历数组：for (int i = 0; i < anArray.length; i++)。
 * 8. System.out.print() 与 System.out.println() 的区别：
 *    - print() 输出后不换行
 *    - println() 输出后换行
 */
package chp3_base.exp3_15;                              // 包声明，该文件位于 chp3_base.exp3_15 包中
public class ArrayDemo {                                // 声明一个公共类 ArrayDemo
    public static void main(String[] args) {             // 主方法，程序执行的入口
        int[] anArray;                                   // 声明一个 int 类型的数组引用变量（此时未分配内存空间）
        anArray = new int[10];                           // 创建包含 10 个 int 元素的数组，在堆中分配内存
        // 为数组的每个元素赋值并打印其值
        for (int i = 0; i < anArray.length; i++) {       // 遍历数组，从索引 0 到 length-1
            anArray[i] = i;                              // 将当前索引 i 的值赋给数组的第 i 个元素
            System.out.print(anArray[i] + " ");          // 打印当前元素的值，并在后面加一个空格（不换行）
        }                                                // for 循环结束
        System.out.println();                            // 输出一个空行（换行）
    }                                                    // 主方法结束
}                                                        // 类定义结束
