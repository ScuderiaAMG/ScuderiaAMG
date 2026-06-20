/**
 * 【功能说明】
 * 本程序演示 switch-case 语句中的"穿透（fall-through）"特性。
 * 程序根据月份（month）和年份（year）计算该月的天数。
 * 多个 case 可以共用一个执行体（无 break 时依次穿透），
 * 节省代码量。对于 2 月，还通过闰年判断逻辑确定是 28 天还是 29 天。
 *
 * 【知识点】
 * 1. switch 的穿透（fall-through）：当一个 case 分支没有 break 时，
 *    程序会继续执行下一个 case 的代码，直到遇到 break 或 switch 结束。
 * 2. 利用穿透可以合并多个 case 值到同一处理逻辑（如 1,3,5,7,8,10,12 月均为 31 天）。
 * 3. 闰年判断公式：能被 4 整除但不能被 100 整除，
 *    或者能被 400 整除的年份为闰年。
 * 4. 逻辑运算符：&&（与）、||（或）、!（非）。
 * 5. 取模运算符 %：计算余数，用于判断能否整除。
 * 6. 多层条件判断：((year % 4 == 0) && !(year % 100 == 0)) || (year % 400 == 0)。
 */
package chp3_base.exp3_10;                               // 包声明，该类位于 chp3_base.exp3_10 包中
public class SwitchDemo2 {                               // 公共类 SwitchDemo2
    public static void main(String[] args) {             // main 方法：程序入口
        int month = 2;                   // 声明 int 变量 month 并赋值为 2（代表二月）
        int year = 2000;                 // 声明 int 变量 year 并赋值为 2000（测试闰年）
        int numDays = 0;                 // 声明 int 变量 numDays 并初始化为 0（存放天数结果）
        switch (month) {                 // switch 语句：根据 month 的值进行分支匹配
        case 1:                          // 1 月（穿透到 case 3，因无 break）
        case 3:                          // 3 月（穿透到 case 5）
        case 5:                          // 5 月（穿透到 case 7）
        case 7:                          // 7 月（穿透到 case 8）
        case 8:                          // 8 月（穿透到 case 10）
        case 10:                         // 10 月（穿透到 case 12）
        case 12:                         // 12 月（所有大月汇聚到此）
            numDays = 31;                // 大月天数为 31 天
            break;                       // break：跳出 switch
        case 4:                          // 4 月（穿透到 case 6）
        case 6:                          // 6 月（穿透到 case 9）
        case 9:                          // 9 月（穿透到 case 11）
        case 11:                         // 11 月（所有小月汇聚到此）
            numDays = 30;                // 小月天数为 30 天
            break;                       // break：跳出 switch
        case 2:                          // 2 月（需要根据闰年判断天数）
            if (((year % 4 == 0) && !(year % 100 == 0)) || (year % 400 == 0)) // 闰年判断条件
                numDays = 29;            // 闰年 2 月有 29 天
            else                         // 否则（平年）
                numDays = 28;            // 平年 2 月有 28 天
            break;                       // break：跳出 switch
        }                                // switch 语句结束
        System.out.println("The date is 2000.2. The number of Days = " // 输出提示信息
                + numDays);              // 拼接并输出 numDays 的值（2000 年为闰年，输出 29）
    }                                                    // main 方法结束
}                                                        // 类定义结束
