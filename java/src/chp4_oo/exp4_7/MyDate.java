/**
 * 【功能说明】
 * 本文件演示了Java中类的构造方法、this关键字以及对象方法的简单应用。
 * 定义了一个MyDate（日期）类，包含日、月、年三个私有成员变量。
 * 提供了带参数的构造方法来初始化日期对象，以及一个tomorrow方法
 * 用于计算并返回"明天"的日期字符串（将day加1，不考虑月份和年份的进位）。
 *
 * 【知识点】
 * 1. 构造方法重载：构造方法也可以有参数列表，用于在创建对象时初始化成员变量
 * 2. this关键字：在构造方法中，this用于区分成员变量和参数（形参与成员变量同名时）
 * 3. 成员变量的私有封装：使用private修饰成员变量，通过公有方法访问
 * 4. 对象方法的定义与调用：定义非静态方法，通过对象引用调用
 * 5. 字符串拼接：使用"+"操作符将不同类型的数据拼接成字符串
 * 6. 简化声明：private int day, month, year; 一次声明多个同类型变量
 * 7. new关键字的完整使用：new 类名(参数) — 创建对象并调用带参构造方法
 */
package chp4_oo.exp4_7;                     // 声明包路径，该类属于chp4_oo.exp4_7包

/**
 * MyDate类：日期类
 * 封装了年、月、日的日期信息，提供构造方法初始化和计算明天日期的方法
 */
public class MyDate {                        // 定义一个名为MyDate的公共类

    // 在一行中声明三个同类型的私有成员变量（简化写法）
    private int day, month, year;            // day:日, month:月, year:年，均为private访问权限

    /**
     * 带参数的构造方法
     * 使用this关键字区分成员变量和参数（形参与成员变量同名）
     * @param day   日
     * @param month 月
     * @param year  年
     */
    public MyDate(int day, int month, int year) { // 构造方法，参数与成员变量同名
        this.day = day;                      // this.day表示成员变量day，= day表示参数day的值
        this.month = month;                  // this.month表示成员变量month，= month表示参数month的值
        this.year = year;                    // this.year表示成员变量year，= year表示参数year的值
    }                                        // 构造方法结束，对象初始化完成

    /**
     * tomorrow方法：计算明天的日期
     * 将day加1（不考虑月份和年份的进位，仅为演示目的）
     * 注意：这是一个简化的实现，不考虑每月的天数差异和年份边界
     * @return 明天日期的字符串，格式为"日/月/年"
     */
    public String tomorrow() {               // 公有方法，返回明天的日期字符串
        day = day + 1;                       // 将成员变量day加1，表示"明天"的日
        // 返回格式化的日期字符串（简化实现，不考虑跨月/跨年的情况）
        return day + "/" + month + "/" + year;
        // 注意：day的值已被永久修改，再次调用tomorrow()会在新值基础上再加1
    }

    /**
     * main方法：Java程序入口点
     * 创建MyDate对象并测试tomorrow方法
     * @param args 命令行参数数组
     */
    public static void main(String[] args) { // 主方法，JVM自动调用
        // 创建MyDate对象，调用带参构造方法，设置日期为2009年4月12日
        MyDate d = new MyDate(12, 4, 2009);

        // 调用tomorrow方法，计算明天的日期并输出
        System.out.println(d.tomorrow());
        // 方法内部：day从12变为13，month和year不变
        // 输出：13/4/2009
    }
}
