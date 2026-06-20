/**
 * 【功能说明】
 * 本程序演示 do-while 循环的基本用法，与 WhileDemo 功能相同但使用不同的循环结构。
 * 程序从字符串 "Copy this string until you encounter the letter 'g'" 中逐字符读取，
 * 使用 StringBuffer 将字符依次追加，直到遇到字符 'g' 时停止循环，最后输出累积结果。
 * 与 while 循环的关键区别在于：do-while 保证循环体至少执行一次。
 *
 * 【知识点】
 * 1. do-while 循环：先执行一次循环体，再判断条件表达式。
 *    条件为 true 继续执行，false 则退出循环。循环体至少执行一次。
 * 2. while 循环 vs do-while 循环：while 是先判断后执行，可能一次都不执行；
 *    do-while 是先执行后判断，至少执行一次。
 * 3. String.charAt(int index)：获取字符串指定索引处的字符。
 * 4. StringBuffer.append(char)：将字符追加到可变字符串末尾。
 * 5. ++i（前缀自增）：先自增再使用新值。
 */
package chp3_base.exp3_7;                               // 包声明，该类位于 chp3_base.exp3_7 包中
public class DoWhileDemo {                               // 公共类 DoWhileDemo
    public static void main(String[] args) {             // main 方法：程序入口
        String copyFromMe = "Copy this string until you encounter the letter 'g'"; // 源字符串定义
        StringBuffer copyToMe = new StringBuffer();      // 创建 StringBuffer 对象，用于累积字符
        int i = 0;                     // 声明并初始化索引变量 i，从 0 开始
        char c = copyFromMe.charAt(i); // 获取源字符串第一个字符（索引 0），赋值给 c
        do {                           // do 关键字：开始 do-while 循环，先执行循环体
            copyToMe.append(c);        // 将当前字符 c 追加到 StringBuffer 的末尾
            c = copyFromMe.charAt(++i); // 前缀自增 i，然后获取下一个字符赋给 c
        } while (c != 'g');            // while 条件判断：若 c 不是 'g' 则继续循环，否则退出
        System.out.println(copyToMe);  // 输出 StringBuffer 中累积的字符串（不包含 'g' 本身）
    }                                                    // main 方法结束
}                                                        // 类定义结束
