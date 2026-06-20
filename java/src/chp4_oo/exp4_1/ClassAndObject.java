/**
 * 【功能说明】
 * 本文件演示了Java中类和对象的基本概念。
 * 定义了一个EmpInfo（员工信息）类，包含姓名、职位和部门三个属性，
 * 以及一个构造方法和一个打印方法。在ClassAndObject的主方法中，
 * 创建了两个EmpInfo对象并调用其打印方法输出员工信息。
 *
 * 【知识点】
 * 1. 类的定义：使用class关键字定义类，类是对象的模板
 * 2. 成员变量（属性）：定义在类中的变量，描述对象的状态
 * 3. 构造方法：与类名相同的方法，用于初始化对象，没有返回类型
 * 4. 对象创建：使用new关键字调用构造方法来创建对象实例
 * 5. 方法调用：通过对象引用调用对象的方法（点操作符）
 * 6. 包声明：package语句用于将类组织到包中
 * 7. 默认访问权限：不加访问修饰符时，类成员具有包级可见性（default）
 */
package chp4_oo.exp4_1;                     // 声明包路径，该类属于chp4_oo.exp4_1包

/**
 * EmpInfo类：员工信息类
 * 演示了类的定义，包含成员变量和构造方法
 */
class EmpInfo {                              // 定义一个名为EmpInfo的类（默认访问权限，同一包内可见）
    String name;                             // 声明String类型成员变量name，用于存储员工姓名
    String designation;                      // 声明String类型成员变量designation，用于存储员工职位
    String department;                       // 声明String类型成员变量department，用于存储员工所属部门

    /**
     * EmpInfo类的构造方法
     * 用于创建EmpInfo对象时初始化成员变量
     * @param eName   员工姓名
     * @param eDesign 员工职位
     * @param eDept   员工部门
     */
    public EmpInfo(String eName, String eDesign, String eDept) {
        // 构造方法：与类名相同，无返回类型，用public修饰表示公开访问
        name = eName;                        // 将构造方法参数eName的值赋给成员变量name
        designation = eDesign;               // 将构造方法参数eDesign的值赋给成员变量designation
        department = eDept;                  // 将构造方法参数eDept的值赋给成员变量department
    }

    /**
     * print方法：打印员工信息到控制台
     * 无参数，无返回值(void)，访问权限为默认（包级可见）
     */
    void print() {                           // 定义print方法，无返回值
        System.out.println(name + " is a " + // 使用System.out.println输出员工姓名 + 固定字符串
                designation + " at " + department + ".");  // 拼接职位、部门和句号，形成完整描述
    }
}

/**
 * ClassAndObject类：包含main方法的主类
 * 演示了如何创建对象（类的实例化）以及调用对象方法
 * 该类被声明为public，表示可以从其他包访问
 */
public class ClassAndObject {                // 定义一个名为ClassAndObject的公共类
    /**
     * main方法：Java程序的入口点
     * JVM会自动调用此方法来启动程序
     * @param args 命令行参数数组
     */
    public static void main(String args[]) { // 主方法，public表示公开，static表示静态（无需实例化即可调用）
        // 使用new关键字创建EmpInfo类的第一个对象实例e1，并调用构造方法传入参数
        EmpInfo e1 = new EmpInfo("Robert Java", "Manager", "Coffee shop");
        // 创建EmpInfo类的第二个对象实例e2
        EmpInfo e2 = new EmpInfo("Tom Java", "Worker", "Coffee shop");

        e1.print();                          // 通过对象引用e1调用print方法，输出e1的员工信息
        e2.print();                          // 通过对象引用e2调用print方法，输出e2的员工信息
    }
}
