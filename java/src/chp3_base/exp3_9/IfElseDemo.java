/**
 * 【功能说明】
 * 本程序演示 if-else if-else 多分支条件语句的用法以及三元条件运算符的使用。
 * 程序根据一个整数考试成绩（testScore）按分数段评定等级：
 * >= 90 为 'A'，>= 80 为 'B'，>= 70 为 'C'，>= 60 为 'D'，< 60 为 'E'。
 * 最后输出等级，并使用三元运算符判断该等级字母是否为大写字母。
 *
 * 【知识点】
 * 1. if-else if-else 多分支结构：从上到下依次判断，遇到第一个 true 的条件
 *    则执行对应的分支，执行完后跳过整个 if-else 结构。
 * 2. 条件判断的顺序非常重要：条件应从严格到宽松排列（如 >=90 在 >=80 之前），
 *    否则可能得不到预期的分支结果。
 * 3. 三元（条件）运算符：条件 ? 表达式1 : 表达式2。
 *    条件为 true 时取表达式1的值，否则取表达式2的值。
 * 4. Character.isUpperCase(char)：Character 包装类的静态方法，
 *    判断指定字符是否为大写字母（'A'~'Z'），返回 boolean 值。
 * 5. char 类型与 String 的拼接：char 在字符串连接时转为字符本身。
 */
package chp3_base.exp3_9;                               // 包声明，该类位于 chp3_base.exp3_9 包中
public class IfElseDemo {                                // 公共类 IfElseDemo
    public static void main(String[] args) {             // main 方法：程序入口
        int testScore = 76;              // 声明 int 变量 testScore 并赋值为 76（模拟考试成绩）
        char grade;                      // 声明 char 变量 grade，用于存放评定的等级
        if (testScore >= 90) {           // 如果分数 >= 90（最高分段）
            grade = 'A';                 // 等级为 A（优秀）
        } else if (testScore >= 80) {    // 否则如果分数 >= 80（第二个分段）
            grade = 'B';                 // 等级为 B（良好）
        } else if (testScore >= 70) {    // 否则如果分数 >= 70（第三个分段）
            grade = 'C';                 // 等级为 C（中等，由于 testScore=76，此分支被执行）
        } else if (testScore >= 60) {    // 否则如果分数 >= 60（第四个分段）
            grade = 'D';                 // 等级为 D（及格）
        } else {                         // 以上条件均不满足（即分数 < 60）
            grade = 'E';                 // 等级为 E（不及格）
        }                                // if-else 结构结束
        System.out.println("Grade = " + grade);          // 输出评定的等级
        System.out.println("The character "+grade+" is "+         // 输出包含等级字符的字符串
        (Character.isUpperCase(grade)?"upper":"lower")+"case.");  // 三元运算符：若 grade 为大写字母则输出 "upper"，否则 "lower"
    }                                                    // main 方法结束
}                                                        // 类定义结束
