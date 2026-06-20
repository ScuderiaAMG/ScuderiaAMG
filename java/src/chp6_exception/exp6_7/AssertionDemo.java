/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了Java中断言（assert）机制的用法。
 * 程序定义了一个月份变量 month = 13，并在 switch 语句中
 * 对各月份进行匹配输出。default 分支中使用了
 * assert false : "Hey, that's not a valid month!" 断言，
 * 当执行到 default 分支时，断言条件 false 恒不成立，
 * 因此会抛出 AssertionError。
 * ⚠ 注意：断言默认是禁用的，运行时需加 -ea 参数开启：
 *    java -ea AssertionDemo
 * 若不开启断言，程序仅打印 "false" 并正常结束。
 *
 * 【知识点】
 * 1. assert 关键字：Java 1.4 引入的断言机制
 * 2. assert 语法：assert 条件; 或 assert 条件:"消息";
 * 3. AssertionError：断言失败时抛出的错误（Error子类）
 * 4. 断言的启用/禁用：-ea / -da JVM参数
 * 5. switch-case 选择结构及 default 分支
 * 6. 断言适用于开发和测试阶段，不应依赖断言影响程序逻辑
 * 7. 断言失败时第二个表达式作为错误信息传递给 AssertionError
 * ============================================================
 */
package chp6_exception.exp6_7;                             // 声明包路径，属于第6章异常处理实验7

public class AssertionDemo {                               // 定义公开类AssertionDemo
    public static void main(String[] args) {               // 程序入口点
        int month = 13;                                    // 定义月份变量并赋值为13（无效月份，将触发default分支）
        switch (month) {                                   // switch选择结构，根据month的值进行分支匹配
            case 1:                                        // case 1: 一月
                System.out.println("January");             // 打印"January"
                break;                                     // 跳出switch结构
            case 2:                                        // case 2: 二月
                System.out.println("February");            // 打印"February"
                break;                                     // 跳出switch结构
            case 3:                                        // case 3: 三月
                System.out.println("March");               // 打印"March"
                break;                                     // 跳出switch结构
            case 4:                                        // case 4: 四月
                System.out.println("April");               // 打印"April"
                break;                                     // 跳出switch结构
            case 5:                                        // case 5: 五月
                System.out.println("May");                 // 打印"May"
                break;                                     // 跳出switch结构
            case 6:                                        // case 6: 六月
                System.out.println("June");                // 打印"June"
                break;                                     // 跳出switch结构
            case 7:                                        // case 7: 七月
                System.out.println("July");                // 打印"July"
                break;                                     // 跳出switch结构
            case 8:                                        // case 8: 八月
                System.out.println("August");              // 打印"August"
                break;                                     // 跳出switch结构
            case 9:                                        // case 9: 九月
                System.out.println("September");           // 打印"September"
                break;                                     // 跳出switch结构
            case 10:                                       // case 10: 十月
                System.out.println("October");             // 打印"October"
                break;                                     // 跳出switch结构
            case 11:                                       // case 11: 十一月
                System.out.println("November");            // 打印"November"
                break;                                     // 跳出switch结构
            case 12:                                       // case 12: 十二月
                System.out.println("December");            // 打印"December"
                break;                                     // 跳出switch结构
            default:                                       // default分支：当月份不在1-12范围内时执行
                System.out.println("false");               // 先打印"false"
                assert false : "Hey, that's not a valid month!"; // 断言条件为false，抛出AssertionError并附带消息
                break;                                     // 跳出switch结构（若断言启用，此行不会执行到）
        }                                                  // switch结构结束
    }                                                      // main方法结束
}                                                          // 类定义结束
