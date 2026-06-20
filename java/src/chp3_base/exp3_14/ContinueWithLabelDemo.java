/**
 * 【功能说明】
 * 本程序演示了 Java 中带标签的 continue 语句（Labeled Continue）的用法。
 * 程序在长字符串中搜索子字符串，通过带标签的 continue 实现：
 * 当匹配失败时跳过当前外层循环的剩余部分，直接进入下一次外层循环迭代。
 * 当完全匹配时，设置标志位并通过带标签的 break 终止外层循环。
 *
 * 【知识点】
 * 1. 带标签的 continue 语句：continue label 可以跳过指定标签所在循环的当前迭代，
 *    并直接进入该标签标记的循环的下一次迭代。
 * 2. 带标签的 continue 与带标签的 break 的区别：
 *    - continue label：跳过当前迭代，继续下一次迭代
 *    - break label：完全终止标签标记的循环
 * 3. 字符串中查找子串的手动实现逻辑：
 *    - 外层循环遍历主串的每个可能的起始位置
 *    - 内层循环逐字符比较子串是否匹配
 * 4. 三元运算符：condition ? value1 : value2
 * 5. 后置自增运算符：j++ 表示先使用 j 的当前值，再将其加 1
 * 6. n-- 作为循环条件：先判断 n 是否为 0，再将 n 减 1
 */
package chp3_base.exp3_14;                              // 包声明，该文件位于 chp3_base.exp3_14 包中
public class ContinueWithLabelDemo {                    // 声明一个公共类 ContinueWithLabelDemo
    public static void main(String[] args) {             // 主方法，程序执行的入口
        String searchMe = "Look for a substring in me"; // 定义被搜索的长字符串
        String subString = "sub";                       // 定义要查找的子字符串
        boolean foundIt = false;                        // 布尔标志位，记录是否找到了子串
        int max = searchMe.length() - subString.length();// 最大起始索引位置（保证从该位置开始子串不会超出主串范围）
        test: for (int i = 0; i < max; i++) {           // 标签 test 标记外层循环；遍历每个可能的起始位置
            int n = subString.length();                 // 获取子串的长度，用于内层逐字符比较
            int j = i;                                  // j 指向主串中当前正在比较的字符位置（从 i 开始）
            int k = 0;                                  // k 指向子串中当前正在比较的字符位置（从 0 开始）
            while (n-- != 0) {                          // 循环 n 次（n 从子串长度递减到 1），逐字符比较
                if (searchMe.charAt(j++)                 // 比较主串中位置 j 和子串中位置 k 的字符
                        != subString.charAt(k++)) {
                    continue test;                      // 如果字符不匹配，带标签的 continue 回到外层循环的下一轮迭代
                }                                       // 内层 if 代码块结束
            }                                           // while 循环结束（执行到这里说明子串完全匹配）
            foundIt = true;                             // 设置找到标志位为 true
            break test;                                 // 带标签的 break 终止外层循环（已经找到，无需继续搜索）
        }                                               // 外层 for 循环结束
        System.out.println(foundIt ? "Found it"         // 使用三元运算符根据 foundIt 输出相应结果
                : "Didn't find it");
    }                                                   // 主方法结束
}                                                       // 类定义结束
