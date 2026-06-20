/**
 * 【功能说明】
 * 本文件演示了Java中简单的类设计与封装，包括构造方法、Getter/Setter方法
 * 以及对象的基本使用。定义了一个Dog（狗）类，包含name（名字）属性，
 * 提供了带参构造方法、getName和setName方法。UseDog类创建Dog对象，
 * 调用setter方法修改名字，然后调用getter方法获取并输出名字。
 *
 * 【知识点】
 * 1. 类的封装：将数据（name）声明为默认访问权限，通过公有方法访问
 * 2. 构造方法：与类名相同，用于创建对象时初始化成员变量
 * 3. this关键字：在构造方法和setter方法中区分参数与成员变量
 * 4. Getter方法：用于获取私有/受保护成员变量的值
 * 5. Setter方法：用于修改私有/受保护成员变量的值
 * 6. 对象的创建与方法的调用：new + 构造方法 创建对象，点操作符调用方法
 * 7. 默认访问权限（包级可见）：不加访问修饰符时，类成员在同一包内可访问
 */
package chp4_oo.exp4_8;                     // 声明包路径，该类属于chp4_oo.exp4_8包

/**
 * Dog类：狗类
 * 包含名字属性及对应的Getter和Setter方法
 */
class Dog {                                  // 定义一个名为Dog的类（默认访问权限，包级可见）
    String name;                             // 成员变量name，表示狗的名字，默认访问权限

    /**
     * Dog类的构造方法
     * 用于创建Dog对象时指定名字
     * @param name 狗的名字
     */
    Dog(String name) {                       // 构造方法，参数name表示狗的新名字（与成员变量同名）
        this.name = name;                    // this.name表示成员变量，= name表示参数的值
    }                                        // 构造方法结束，name被初始化

    /**
     * getName方法：获取狗的名字
     * @return 当前狗的名字字符串
     */
    String getName() {                       // Getter方法，返回成员变量name的值
        return name;                         // 返回当前对象的name
    }

    /**
     * setName方法：设置狗的名字
     * @param name 要设置的新名字
     */
    void setName(String name) {              // Setter方法，用于修改成员变量name的值
        this.name = name;                    // this.name表示成员变量，= name表示参数的值
    }
}

/**
 * UseDog类：包含main方法的主类
 * 演示如何创建Dog对象、调用setter和getter方法
 */
public class UseDog {                        // 定义一个名为UseDog的公共类

    /**
     * main方法：Java程序入口点
     * 创建Dog对象，修改名字并输出
     * @param args 命令行参数数组
     */
    public static void main(String[] args) { // 主方法，JVM自动调用
        // 创建Dog对象，调用带参构造方法，初始名字为"����"
        Dog d = new Dog("����");

        // 调用setName方法，将狗的名字修改为"Сǿ"
        d.setName("Сǿ");

        // 调用getName方法获取修改后的名字，并拼接后输出
        System.out.println("The dog's name is " + d.getName());
        // 输出：The dog's name is Сǿ
    }
}
