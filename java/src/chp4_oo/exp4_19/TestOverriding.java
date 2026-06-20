/**
 * 【功能说明】
 * 本文件演示了Java中的方法重写（Method Overriding）。
 * Employee类是一个基础员工类，包含name和salary属性以及getDetails()方法。
 * Manager类继承自Employee，重写了getDetails()方法，在父类返回信息的基础上
 * 追加了department（部门）信息。
 * Secretary类继承自Employee，但没有重写getDetails()方法，因此直接使用
 * 从父类继承而来的实现。
 * TestOverriding类的main方法创建Manager和Secretary对象，并分别调用
 * 它们的getDetails()方法，展示了Java动态绑定（Dynamic Binding）的特性——
 * JVM在运行时根据对象的实际类型来决定调用哪个版本的方法。
 *
 * 【知识点】
 * 1. 方法重写（Method Overriding）—— 子类重新定义父类中已有的方法
 * 2. 重写的要求：方法名、参数列表、返回类型必须相同（或返回类型是子类型）
 * 3. 动态绑定（Dynamic Binding）—— 运行时根据对象实际类型决定调用哪个方法
 * 4. 如果一个子类没有重写父类的方法，则会继承并使用父类的方法实现
 * 5. @Override注解（可选的）用于在编译时检查是否正确地重写了父类方法
 * 6. 重写与重载（Overloading）的区别：重写是运行时多态，重载是编译时多态
 */
package chp4_oo.exp4_19;  // 包声明，表明当前类位于chp4_oo.exp4_19包中

/**
 * Employee类——基础员工类，是所有员工类的父类
 */
class Employee {
    // 员工姓名（默认访问权限，即包级别访问权限，子类可以访问）
    String name ;
    // 员工薪资（默认访问权限，即包级别访问权限，子类可以访问）
    int salary;

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
     * 父类中的原始方法，子类可以选择重写它
     * @return 包含姓名和薪资的格式化字符串
     */
    public String getDetails( ){
        return "Name: "+name+"\nSalary: "+salary;  // 返回"Name: xxx\nSalary: xxx"格式的字符串
    }
}

/**
 * Manager类——经理类，继承自Employee类
 * 重写了getDetails()方法以提供更多信息
 */
class Manager extends Employee {
    // 部门名称（子类新增的私有成员变量）
    private String department ;

    /**
     * Manager类的有参构造方法
     * @param name       经理姓名
     * @param salary     经理薪资
     * @param department 经理所属部门
     */
    public Manager(String name,int salary,String department){
        super(name,salary);       // 调用父类Employee的有参构造方法
        this.department = department; // 初始化子类新增的部门属性
    }

    /**
     * 重写父类的getDetails()方法
     * 在父类返回的姓名和薪资信息基础上，追加部门信息
     * @return 包含姓名、薪资和部门的格式化字符串
     */
    public String getDetails( ){
        // 注意：此处直接访问了父类的name和salary成员（因为它们具有包访问权限）
        return "Name: "+name+"\nSalary: "+salary+"\nDepartment: "+ department;
    }
}

/**
 * Secretary类——秘书类，继承自Employee类
 * 没有重写getDetails()方法，直接继承父类的实现
 */
class Secretary extends Employee{
    /**
     * Secretary类的有参构造方法
     * @param name   秘书姓名
     * @param salary 秘书薪资
     */
    public Secretary(String name,int salary){
        super(name,salary);  // 调用父类Employee的有参构造方法
    }
    // 没有重写getDetails()方法，会直接继承Employee类的getDetails()方法
}

/**
 * TestOverriding类——测试类，包含main方法作为程序入口
 * 演示方法重写和动态绑定
 */
public class TestOverriding{
    /**
     * 主方法，程序的入口
     * @param srgs 命令行参数数组
     */
    public static void main(String[] srgs){
        // 创建Manager对象，传入姓名"Tom"、薪资2000和部门"Finance"
        Manager m = new Manager("Tom",2000,"Finance");
        // 创建Secretary对象，传入姓名"Mary"和薪资1500
        Secretary s = new Secretary("Mary",1500);

        // 调用Manager对象的getDetails()方法——实际执行Manager类中重写的版本
        System.out.println(m.getDetails());
        // 调用Secretary对象的getDetails()方法——Secretary没有重写，执行Employee类的版本
        System.out.println(s.getDetails());
    }
}
