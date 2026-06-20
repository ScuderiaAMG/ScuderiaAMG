/**
 * 【功能说明】
 * 本程序演示 switch-case 多分支选择语句的基本用法。
 * 程序根据 month 变量的值（1~12），使用 switch 语句匹配对应的 case 分支，
 * 输出对应月份的英文名称。当 month 的值不在 1~12 范围内时，
 * 执行 default 分支，输出错误提示信息。
 *
 * 【知识点】
 * 1. switch 语句：根据表达式的值选择匹配的 case 分支执行。
 * 2. case 子句后的值必须是编译期常量（字面量或常量表达式）。
 * 3. break 关键字：跳出 switch 语句，防止"穿透（fall-through）"。
 *    若省略 break，会继续执行下一个 case 的代码，直到遇到 break 或 switch 结束。
 * 4. default 子句（可选）：当所有 case 都不匹配时执行，通常放在最后。
 * 5. switch 表达式支持的类型：byte、short、char、int、枚举（Enum）、
 *    String（JDK 7+）。
 * 6. 每个 case 后的代码应尽量以 break 结束，避免意外的穿透行为。
 */
package chp3_base.exp3_10;                               // 包声明，该类位于 chp3_base.exp3_10 包中
public class SwitchDemo {                                // 公共类 SwitchDemo
    public static void main(String[] args) {             // main 方法：程序入口
        int month = 8;                   // 声明 int 变量 month 并赋值为 8（代表 8 月）
        switch (month) {                 // switch 语句开始，根据 month 的值进行分支匹配
        case 1:                          // 如果 month 等于 1
            System.out.println("January");   // 输出 "January"（一月）
            break;                       // break：跳出整个 switch 语句，防止穿透到下一个 case
        case 2:                          // 如果 month 等于 2
            System.out.println("February");  // 输出 "February"（二月）
            break;
        case 3:                          // 如果 month 等于 3
            System.out.println("March");     // 输出 "March"（三月）
            break;
        case 4:                          // 如果 month 等于 4
            System.out.println("April");     // 输出 "April"（四月）
            break;
        case 5:                          // 如果 month 等于 5
            System.out.println("May");       // 输出 "May"（五月）
            break;
        case 6:                          // 如果 month 等于 6
            System.out.println("June");      // 输出 "June"（六月）
            break;
        case 7:                          // 如果 month 等于 7
            System.out.println("July");      // 输出 "July"（七月）
            break;
        case 8:                          // 如果 month 等于 8（匹配成功，因为 month = 8）
            System.out.println("August");    // 输出 "August"（八月）
            break;                       // break 跳出 switch
        case 9:                          // 如果 month 等于 9
            System.out.println("September"); // 输出 "September"（九月）
            break;
        case 10:                         // 如果 month 等于 10
            System.out.println("October");   // 输出 "October"（十月）
            break;
        case 11:                         // 如果 month 等于 11
            System.out.println("November");  // 输出 "November"（十一月）
            break;
        case 12:                         // 如果 month 等于 12
            System.out.println("December");  // 输出 "December"（十二月）
            break;
        default:                         // 如果 month 的值与所有 case 都不匹配
            System.out.println("Hey, that's not a valid month!"); // 输出错误提示
            break;                       // break 跳出 switch（default 通常也是以 break 结尾）
        }                                // switch 语句结束
    }                                                    // main 方法结束
}                                                        // 类定义结束
