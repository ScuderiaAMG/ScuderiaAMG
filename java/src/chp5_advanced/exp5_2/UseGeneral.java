/**
 * 【功能说明】
 * 本程序演示了Java中静态方法（static method）的用法。
 * GeneralFunction类中定义了一个静态方法add，用于计算两个整数的和。
 * 在UseGeneral类的main方法中，直接通过"类名.方法名"的方式调用
 * 静态方法，无需创建GeneralFunction类的对象实例。
 *
 * 【知识点】
 * 1. static方法（类方法）：属于类本身，可通过类名直接调用
 * 2. 静态方法不能直接访问非静态的实例变量或实例方法
 * 3. 静态方法常被用作工具方法（utility method），如Math类中的各种数学函数
 * 4. 静态方法调用语法：ClassName.staticMethodName(args)
 * 5. main方法必须是public static void，因为JVM需要在没有对象的情况下调用它
 */
package chp5_advanced.exp5_2;                              // 声明包路径，该文件位于chp5_advanced.exp5_2包中

class GeneralFunction {                                    // 定义一个通用工具类GeneralFunction
    public static int add(int x, int y) {                  // 静态方法add：返回两个整数的和
        return x + y;                                      // 返回参数x与y的和
    }
}

public class UseGeneral {                                  // 主类（public），包含程序入口main方法
    public static void main(String[] args) {               // 主方法：程序执行的入口点
        int c = GeneralFunction.add(9, 10);                // 通过类名直接调用静态方法add，无需创建对象，将返回值赋给变量c
        System.out.println("9 + 10 = " + c);               // 输出计算结果："9 + 10 = 19"
    }
}
