/**
 * 【功能说明】
 * 本程序演示了 Java 中 continue 语句的用法。
 * 程序遍历一个字符串，统计其中字母 'p'（小写）出现的次数，
 * 并将每个小写 'p' 替换为大写 'P'。
 * 当遇到非 'p' 字符时，使用 continue 跳过当前循环的剩余代码，进入下一次循环。
 *
 * 【知识点】
 * 1. continue 语句：用于跳过当前循环迭代中剩余的代码，直接进入下一次迭代。
 * 2. StringBuffer 类：可变的字符串缓冲区，支持修改字符串内容（与 String 不同，String 是不可变的）。
 * 3. StringBuffer.charAt(int index)：获取指定索引位置的字符。
 * 4. StringBuffer.setCharAt(int index, char ch)：修改指定索引位置的字符。
 * 5. StringBuffer.length()：获取字符串长度。
 * 6. for 循环遍历字符串的每个字符。
 * 7. continue 与 break 的区别：
 *    - continue 跳过当前迭代的剩余部分，进入下一次迭代
 *    - break 直接终止整个循环
 */
package chp3_base.exp3_13;                              // 包声明，该文件位于 chp3_base.exp3_13 包中
public class ContinueDemo {                             // 声明一个公共类 ContinueDemo
    public static void main(String[] args) {             // 主方法，程序执行的入口
        StringBuffer searchMe = new StringBuffer(       // 创建一个 StringBuffer 对象，内容为一串英文绕口令
                "peter piper picked a peck of pickled peppers");
        int max = searchMe.length();                    // 获取字符串的总长度并存入 max
        int numPs = 0;                                  // 计数器，用于统计小写字母 'p' 的个数
        for (int i = 0; i < max; i++) {                 // 从索引 0 到 max-1 遍历字符串的每个字符
            if (searchMe.charAt(i) != 'p')              // 获取当前字符，判断是否不是小写字母 'p'
                continue;                               // 如果不是 'p'，则跳过本次循环的剩余部分，进入下一次循环
            numPs++;                                    // 执行到这里说明当前字符是 'p'，计数器加 1
            searchMe.setCharAt(i, 'P');                 // 将该位置的小写 'p' 替换为大写 'P'
        }                                               // for 循环结束
        System.out.println("Found " + numPs             // 输出统计结果：共找到了多少个 'p'
                + " p's in the string.");
        System.out.println(searchMe);                   // 输出修改后的字符串（小写 p 已被替换为大写 P）
    }                                                   // 主方法结束
}                                                       // 类定义结束
