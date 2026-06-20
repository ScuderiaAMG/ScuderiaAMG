/**
 * 【功能说明】
 * 本程序演示了Java中静态变量（static variable）的用法。
 * 通过Count类中的静态变量counter，实现了为每个Count对象
 * 自动分配递增的序列号（serialNumber）。每次创建新对象时，
 * 静态计数器都会自增并赋值给当前对象的实例变量。
 *
 * 【知识点】
 * 1. static变量（类变量）：被所有实例共享，属于类而不属于某个对象
 * 2. 实例变量（instance variable）：每个对象拥有自己的副本
 * 3. static变量的初始化时机：类加载时初始化，早于任何对象创建
 * 4. static变量常用于实现计数器、ID生成器、常量池等场景
 * 5. 数组的创建与初始化：Count[] cc = new Count[10]
 */
package chp5_advanced.exp5_1;                              // 声明包路径，该文件位于chp5_advanced.exp5_1包中

class Count {                                              // 定义Count类，用于演示静态变量的使用
    private int serialNumber;                              // 实例变量：每个Count对象拥有唯一的序列号
    public static int counter = 0;                         // 静态变量（类变量）：所有Count对象共享，用于生成递增ID，初始值为0

    public Count() {                                       // 构造方法：创建Count对象时调用
        counter++;                                         // 静态变量counter自增1，确保每个对象获得不同的ID
        serialNumber = counter;                            // 将自增后的counter值赋给当前对象的serialNumber实例变量
    }

    public int getSerialNumber() {                         // 公有方法：获取当前对象的序列号值
        return serialNumber;                               // 返回实例变量serialNumber
    }
}

public class TestStaticVar {                               // 主类（public），包含程序入口main方法
    public static void main(String[] args) {               // 主方法：程序执行的入口点
        Count[] cc = new Count[10];                        // 创建Count类型数组，长度为10，用于存放10个Count对象引用
        for (int i = 0; i < cc.length; i++) {              // 使用for循环遍历数组，从索引0到9
            cc[i] = new Count();                           // 创建新的Count对象并赋值给数组元素
            System.out.println("cc[" + i + "].serialNumber = " + cc[i].getSerialNumber()); // 输出当前对象的序列号
        }
    }
}
