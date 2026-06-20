/**
 * 【功能说明】
 * 本程序演示 while 循环的基本用法。
 * 程序从一个字符串 "Copy this string until you encounter the letter 'g'" 中
 * 逐字符读取，使用 StringBuffer 将读取到的字符依次追加，
 * 直到遇到字符 'g' 时停止循环，最后输出已累积的字符串。
 *
 * 【知识点】
 * 1. while 循环：先判断条件表达式，条件为 true 时执行循环体，否则退出。
 * 2. String.charAt(int index)：返回字符串中指定索引位置的字符（索引从 0 开始）。
 * 3. StringBuffer：可变字符串类，可高效地进行字符串追加操作。
 * 4. StringBuffer.append(char)：将字符追加到可变字符串末尾。
 * 5. ++i（前缀自增）：先自增，再使用新值作为索引访问下一个字符。
 * 6. 循环终止条件：遇到字符 'g' 时退出循环（'g' 本身不被追加）。
 */
package chp3_base.exp3_6;                               // 包声明，该类位于 chp3_base.exp3_6 包中
public class WhileDemo {                                 // 公共类 WhileDemo
    public static void main(String[] args) {             // main 方法：程序入口
        String copyFromMe = "Copy this string until you encounter the letter 'g'"; // 定义源字符串，包含目标字符 'g'
        StringBuffer copyToMe = new StringBuffer();      // 创建 StringBuffer 对象，用于高效构建目标字符串
        int i = 0;                     // 声明并初始化索引变量 i，从字符串的第一个字符（索引 0）开始
        char c = copyFromMe.charAt(i); // 获取索引 i 处的字符，将其赋值给变量 c
        while (c != 'g') {             // while 循环：当 c 不是字符 'g' 时继续循环，遇到 'g' 则退出
            copyToMe.append(c);        // 将当前字符 c 追加到 StringBuffer 中
            c = copyFromMe.charAt(++i); // 前缀自增 i（先 i+1，再使用新值），获取下一个字符并赋给 c
        }                              // 循环体结束，回到 while 条件判断
        System.out.println(copyToMe);  // 输出 StringBuffer 中累积的所有字符（遇到 'g' 前的部分）
    }                                                    // main 方法结束
}                                                        // 类定义结束
