/**
 * 【功能说明】
 * 本程序演示 Java 中变量的默认初始化与局部变量的强制性初始化要求。
 * 程序创建一个 TestInit 对象，类中定义的实例变量 x 会自动被赋予默认值 0；
 * main 方法中的局部变量 x 通过 Math.random() 随机产生 0~99 的整数；
 * 局部变量 y 仅在 x > 50 时被赋值，若 x <= 50 则 y 未初始化（会导致编译错误）；
 * 这展示了 Java 编译器对局部变量 "确定赋值"（Definite Assignment）的检查规则。
 *
 * 【知识点】
 * 1. 实例变量（成员变量）的自动初始化为默认值：int → 0。
 * 2. 局部变量不会自动初始化，使用前必须明确赋值，否则编译错误。
 * 3. 确定赋值（Definite Assignment）规则：编译器检查每条执行路径上变量是否都已赋值。
 * 4. Math.random() 方法：返回 [0.0, 1.0) 范围内的随机 double 值。
 * 5. 类型转换（int）强制将 double 截断为 int。
 * 6. 实例变量通过对象名.变量名（init.x）访问。
 * 7. 注意：本程序在 x <= 50 时会编译失败，因为 y 可能未初始化，
 *    正是用于演示"未初始化局部变量不可使用"这一编译规则的典型示例。
 */
package chp3_base.exp3_4;                               // 包声明，指明该类位于 chp3_base.exp3_4 包中
public class TestInit_mimofixed {                                  // 公共类 TestInit
    int x;                          // 实例变量 x（成员变量），未显式赋值，自动初始化为 int 类型的默认值 0
    public static void main(String[] args) {             // main 方法：程序入口
        TestInit_mimofixed init = new TestInit_mimofixed();                  // 创建 TestInit 对象，init.x（实例变量）被默认初始化为 0
        int x = (int) (Math.random() * 100);            // 声明局部变量 x，通过 Math.random() 生成 [0,100) 的随机数并强转为 int
        int z;                         // 声明局部变量 z，尚未初始化
        int y;                         // 声明局部变量 y，尚未初始化
        if (x > 50) {                  // 条件判断：如果 x 大于 50
            y = 9;                     // 则在条件分支内为 y 赋值 9（仅在该路径上 y 被赋值）
        } else {                       // else 分支：确保 y 在所有路径上都被初始化
            y = 0;                     // 当 x <= 50 时，y 赋值为 0
        }                              // if-else 语句结束
        z = x + y + init.x;            // 计算：x + y + init.x，此时 y 已在所有路径上被初始化
        System.out.println("x=" + x + " y=" + y + " z=" + z); // 输出三个变量的值
    }                                                    // main 方法结束
}                                                        // 类定义结束
