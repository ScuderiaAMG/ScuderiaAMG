/**
 * 【功能说明】
 * 本文件演示了Java中封装（Encapsulation）的概念。
 * 定义了一个MyDate（日期）类，将日、月、年三个字段声明为private（私有），
 * 外部只能通过公有的setDate和getDate方法来访问和修改这些字段。
 * UseMyDate类通过调用setDate方法设置日期，并通过返回值判断设置是否成功。
 * 注释部分展示了直接访问私有成员变量的非法操作，以此说明封装的重要性。
 *
 * 【知识点】
 * 1. 封装（Encapsulation）：将数据（成员变量）和行为（方法）绑定在一起，
 *    并对外隐藏内部实现细节
 * 2. private访问修饰符：私有成员只能在本类内部访问，外部类无法直接访问
 * 3. public访问修饰符：公有成员可以被任何其他类访问
 * 4. Getter/Setter方法：通过公有方法间接访问私有成员变量，实现数据控制
 * 5. 数据验证：在setter方法中进行数据合法性检查（如日期范围判断）
 * 6. 返回值表示状态：通过返回不同值（0/-1）来表示操作成功或失败
 * 7. 信息隐藏：外部不能直接操作对象的内部状态，必须通过接口方法
 */
package chp4_oo.exp4_2;                     // 声明包路径，该类属于chp4_oo.exp4_2包

/**
 * MyDate类：自定义日期类
 * 演示了封装性——将成员变量设为private，提供公有方法访问
 */
class MyDate {                               // 定义一个名为MyDate的类（默认访问权限，包级可见）
    private int day;                         // 私有成员变量day，表示日（1-31），仅本类内部可访问
    private int month;                       // 私有成员变量month，表示月份（1-12），仅本类内部可访问
    private int year;                        // 私有成员变量year，表示年份，仅本类内部可访问

    /**
     * getDate方法：获取日期字符串
     * 将日、月、年组合成"日/月/年"格式的字符串返回
     * @return 格式化的日期字符串，如 "22/5/2009"
     */
    public String getDate() {                // 公有方法，供外部获取私有成员变量的值
        return day + "/" + month + "/" + year;  // 返回格式化的日期字符串，"/"作为分隔符
    }

    /**
     * setDate方法：设置日期
     * 在设置之前进行数据合法性验证：
     * - 日必须在1~31之间
     * - 月必须在1~12之间
     * 如果数据合法则设置并返回0，否则返回-1表示设置失败
     * @param a 日
     * @param b 月
     * @param c 年
     * @return 成功返回0，失败返回-1
     */
    public int setDate(int a, int b, int c) { // 公有方法，供外部设置私有成员变量的值
        // 检查数据合法性：日∈[1,31] 且 月∈[1,12]
        if ((a > 0 && a <= 31) && (b > 0 && b <= 12)) {
            day = a;                         // 验证通过，将参数a的值赋给成员变量day
            month = b;                       // 验证通过，将参数b的值赋给成员变量month
            year = c;                        // 验证通过，将参数c的值赋给成员变量year
            return 0;                        // 返回0表示设置成功
        } else {
            return -1;                       // 数据不合法，返回-1表示设置失败
        }
    }
}

/**
 * UseMyDate类：包含main方法的主类
 * 演示了如何通过公有方法安全地访问私有成员变量
 * 展示了正确的封装使用方式（通过方法间接访问）
 * 同时也通过注释展示了错误地直接访问私有成员的方式
 */
public class UseMyDate {                     // 定义一个名为UseMyDate的公共类
    /**
     * main方法：Java程序入口点
     * 创建MyDate对象并通过公有方法操作私有成员变量
     * @param args 命令行参数数组
     */
    public static void main(String[] args) { // 主方法，JVM自动调用
        // 使用new关键字创建MyDate对象实例，调用默认构造方法
        MyDate d = new MyDate();             // 创建MyDate对象，此时day/month/year均为默认值0

        // 调用setDate方法设置日期，并判断返回值是否为0（表示成功）
        if (d.setDate(22, 5, 2009) == 0) {   // 尝试设置日期为2009年5月22日，判断是否设置成功
            // 如果设置成功，则调用getDate方法获取日期字符串并输出到控制台
            System.out.println(d.getDate()); // 输出：22/5/2009
        }

        /*
         * 以下注释代码演示了非法的直接访问私有成员操作。
         * 由于day、month、year被声明为private，
         * 在类外部（UseMyDate类中）无法直接访问这些私有成员，
         * 如果取消注释，编译时将报错。
         *
         * d.day = 22;           // 编译错误：day在MyDate中是private访问权限
         * d.month = 5;          // 编译错误：month在MyDate中是private访问权限
         * d.year = 2009;        // 编译错误：year在MyDate中是private访问权限
         * System.out.println(d.day + "/" + d.month + "/" + d.year);
         *   // 编译错误：无法直接访问私有成员变量
         */
    }
}
