/**
 * 【功能说明】
 * 本文件演示了Java中的继承（Inheritance）和super关键字的使用。
 * Employee类是一个基础员工类，包含name（姓名）和salary（薪资）属性，
 * 以及getDetails()方法返回员工信息。
 * Manager类继承自Employee类，新增了department（部门）属性，
 * 并在构造方法中使用super(name,salary)调用父类构造方法，
 * 同时在重写的getDetails()方法中使用super.getDetails()复用父类方法逻辑。
 * TestSuper类作为测试入口，演示了子类对象的创建和方法的调用。
 *
 * 【知识点】
 * 1. 继承（Inheritance）—— 通过extends关键字实现类之间的继承关系
 * 2. super关键字的两大用途：
 *    a. super(参数) —— 在子类构造方法中调用父类的构造方法（必须是第一行）
 *    b. super.方法名() —— 在子类中调用父类被重写的方法
 * 3. 方法重写（Method Overriding）—— 子类重新定义父类的方法
 * 4. 子类构造方法默认调用父类的无参构造方法，如果父类没有无参构造方法，
 *    则子类必须显式使用super(参数)调用父类的有参构造方法
 */
package chp4_oo.exp4_17;  // 包声明，表明当前类位于chp4_oo.exp4_17包中

/**
 * Employee类——基础员工类，是所有员工类的父类
 */
class Employee {
    private String name ;   // 员工姓名（私有成员，子类不能直接访问）
    private int salary;     // 员工薪资（私有成员，子类不能直接访问）

    /**
     * Employee类的有参构造方法
     * @param name  员工姓名
     * @param salary 员工薪资
     */
    public Employee(String name,int salary){
        this.name = name;     // 使用this关键字区分成员变量和参数
        this.salary = salary; // 将参数salary赋值给成员变量salary
    }

    /**
     * getDetails()方法——返回员工的详细信息字符串
     * @return 包含姓名和薪资的格式化字符串
     */
    public String getDetails( ){
        return "Name: "+name+"\nSalary: "+salary;  // 返回"Name: xxx\nSalary: xxx"格式的字符串
    }
}

/**
 * Manager类——经理类，继承自Employee类，是Employee的子类
 */
class Manager extends Employee {
    private String department ;  // 经理所在的部门（子类新增的成员变量）

    /**
     * Manager类的有参构造方法
     * @param name       经理姓名
     * @param salary     经理薪资
     * @param department 经理所属部门
     */
    public Manager(String name,int salary,String department){
        super(name,salary);       // 调用父类Employee的有参构造方法，初始化继承自父类的属性
        this.department = department; // 初始化子类新增的部门属性
    }

    /**
     * 重写父类的getDetails()方法——在父类方法返回的信息基础上追加部门信息
     * @return 包含姓名、薪资和部门的格式化字符串
     */
    public String getDetails( ){
        // 使用super.getDetails()调用父类被重写的方法，复用父类的逻辑
        return super.getDetails( )+"\nDepartment: "+ department;
    }
}

/**
 * TestSuper类——测试类，包含main方法作为程序入口
 * 演示继承和super关键字的使用
 */
public class TestSuper{
    /**
     * 主方法，程序的入口
     * @param srgs 命令行参数数组
     */
    public static void main(String[] srgs){
        // 创建Manager对象，传入姓名"TOM"、薪资2000和部门"Finance"
        Manager m = new Manager("TOM",2000,"Finance");
        // 调用Manager对象的getDetails()方法（实际执行的是Manager类中重写的版本）
        System.out.println(m.getDetails());
    }
}
