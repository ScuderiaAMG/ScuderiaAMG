/**
 * 【功能说明】
 * 本文件演示了Java中构造方法的重载以及this()构造方法链式调用。
 * Employee（员工）类定义了三个重载的构造方法：
 * - 双参构造方法：初始化姓名和薪水
 * - 单参构造方法：只提供姓名，通过this(n,0)调用双参构造方法，默认薪水为0
 * - 无参构造方法：通过this("Unknown")调用单参构造方法，默认姓名为"Unknown"
 * 这种链式调用模式避免了代码重复。
 *
 * 【知识点】
 * 1. 构造方法重载：一个类可以定义多个参数不同的构造方法
 * 2. this()调用：在一个构造方法中可以使用this(参数)调用另一个重载的构造方法
 * 3. 构造方法链：通过this()实现构造方法之间的链式调用，减少代码重复
 * 4. this()必须是构造方法中的第一条语句
 * 5. 默认值设定：通过无参构造方法提供合理的默认值
 * 6. Getter方法：只提供getter不提供setter实现只读属性（不可变对象的一种实现）
 * 7. 私有成员变量封装：private修饰，外部通过公有方法访问
 */
package chp4_oo.exp4_9;                     // 声明包路径，该类属于chp4_oo.exp4_9包

/**
 * Employee类：员工类
 * 演示构造方法的重载和this()链式调用
 * 包含姓名和薪水两个私有属性，只提供getter方法（不提供setter，实现只读）
 */
class Employee {                             // 定义一个名为Employee的类（默认访问权限）
    private String name;                     // 私有成员变量name，表示员工姓名
    private int salary;                      // 私有成员变量salary，表示员工薪水

    /**
     * 双参构造方法：最完整的构造方法，直接初始化所有成员变量
     * @param n 员工姓名
     * @param s 员工薪水
     */
    public Employee(String n, int s) {       // 构造方法：接收姓名和薪水两个参数
        name = n;                            // 将参数n的值赋给成员变量name
        salary = s;                          // 将参数s的值赋给成员变量salary
    }

    /**
     * 单参构造方法：只提供姓名，通过this(n,0)调用双参构造方法
     * 薪水默认为0
     * @param n 员工姓名
     */
    public Employee(String n) {              // 构造方法：只接收姓名一个参数
        this(n, 0);                          // 使用this()调用双参构造方法，薪水默认传0
    }                                        // 相当于执行了 name=n; salary=0;

    /**
     * 无参构造方法：通过this("Unknown")调用单参构造方法
     * 姓名为"Unknown"，薪水上通过链式调用最终由双参构造方法设为0
     */
    public Employee() {                      // 无参构造方法
        this("Unknown");                     // 使用this()调用单参构造方法，姓名默认传"Unknown"
    }                                        // 最终形成链：this() -> this("Unknown") -> this("Unknown", 0)

    /**
     * getName方法：获取员工姓名
     * @return 员工姓名字符串
     */
    public String getName() {                // Getter方法，返回成员变量name
        return name;                         // 返回当前对象的name值
    }

    /**
     * getSalary方法：获取员工薪水
     * @return 员工薪水（int值）
     */
    public int getSalary() {                 // Getter方法，返回成员变量salary
        return salary;                       // 返回当前对象的salary值
    }
}

/**
 * EmplyeeTest类：包含main方法的主类
 * 演示使用Employee的无参构造方法创建对象并获取属性
 */
public class EmplyeeTest {                   // 定义一个名为EmplyeeTest的公共类

    /**
     * main方法：Java程序入口点
     * 使用无参构造方法创建Employee对象，输出其默认属性值
     * @param args 命令行参数数组
     */
    public static void main(String[] args) { // 主方法，JVM自动调用
        // 使用无参构造方法创建Employee对象
        // 构造方法链：this() -> this("Unknown") -> this("Unknown", 0)
        Employee e = new Employee();         // 创建Employee对象，默认name="Unknown"，salary=0

        // 调用getName和getSalary方法获取属性值并输出
        System.out.println("Name: " + e.getName() + "   Salary: " + e.getSalary());
        // 输出：Name: Unknown   Salary: 0
    }
}
