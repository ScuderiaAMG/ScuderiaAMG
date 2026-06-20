/**
 * 【功能说明】
 * 本程序演示了Java中static变量与final关键字的组合使用。
 * Customer类使用静态变量counter作为全局唯一ID生成器，
 * 使用final修饰的customerID确保每个客户ID在创建后不可改变，
 * 实现了自动分配递增客户编号的功能。
 *
 * 【知识点】
 * 1. final修饰实例变量：表示该变量一旦被赋值后不可修改（常量语义）
 * 2. final实例变量必须在构造方法结束前完成初始化（显式赋值或在构造方法中赋值）
 * 3. static变量用作全局计数器：所有实例共享同一个计数器，实现序列号自增
 * 4. 后缀自增运算符 counter++：先返回counter的当前值再自增1
 * 5. 注意：如果一个类中有main方法，该类必须声明为public（作为程序入口）
 * 6. 本例中Customer类同时也是程序入口主类，main方法直接定义在Customer类中
 */
package chp5_advanced.exp5_4;                              // 声明包路径，该文件位于chp5_advanced.exp5_4包中

class Customer {                                           // 定义Customer（客户）类
    private final long customerID;                         // final修饰的实例变量：客户ID，一旦赋值不可更改
    private static long counter = 200901;                  // 静态变量：全局计数器，从200901开始，用于自动生成客户ID

    public Customer() {                                    // 无参构造方法：创建Customer对象时调用
        customerID = counter++;                            // 将counter的当前值赋给customerID（final变量在此完成初始化），然后counter自增1
    }

    public long getID() {                                  // 公有方法：获取当前客户的ID
        return customerID;                                 // 返回final变量customerID的值
    }

    public static void main(String[] args) {               // 主方法：程序执行的入口点（main直接定义在Customer类中）
        Customer[] cc = new Customer[5];                   // 创建Customer类型数组，长度为5，用于存放5个Customer对象引用
        for (int i = 0; i < cc.length; i++) {              // 使用for循环遍历数组，从索引0到4
            cc[i] = new Customer();                        // 创建新的Customer对象并赋值给数组元素
            System.out.println("The customerID is " + cc[i].getID()); // 输出当前客户的ID
        }
    }
}
