/**
 * 【功能说明】
 * 本程序演示了Java中枚举类型（Enum）和枚举内置方法values()的用法。
 * 定义了一个Week枚举，包含一周七天的枚举常量。
 * 通过调用Week.values()方法获取所有枚举常量的数组，
 * 并使用for-each循环遍历输出每个常量的名称（name()方法）。
 *
 * 【知识点】
 * 1. enum关键字：定义枚举类型，是JDK 5引入的一种特殊的类
 * 2. 枚举常量：枚举中定义的常量列表，都是该枚举类型的实例
 * 3. values()方法：返回该枚举类型所有枚举常量的数组，按声明顺序排列
 * 4. name()方法：返回枚举常量的名称字符串（与声明时的标识符相同）
 * 5. enum隐式继承java.lang.Enum类，自动获得values()、name()、ordinal()等方法
 * 6. for-each循环遍历枚举：for (Week w : Week.values()) 遍历所有枚举常量
 * 7. 枚举是类型安全的：编译期确保传入的枚举值有效
 */
package chp5_advanced.exp5_18;                             // 声明包路径，该文件位于chp5_advanced.exp5_18包中

enum Week {                                                // 定义Week枚举类型，包含一周的七天
    SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY // 枚举常量列表：星期日到星期六
}

public class EnumValuesTest {                              // 主类（public），测试枚举的values()方法
    public static void main(String args[]) {               // 主方法：程序执行的入口点

        for (Week w : Week.values()) {                     // 使用增强for-each循环遍历Week枚举的所有常量值
            System.out.print(w.name() + ". ");             // 调用name()方法获取枚举常量的名称字符串并输出（如"SUNDAY."）
        }
        System.out.println();                              // 输出换行
    }
}
