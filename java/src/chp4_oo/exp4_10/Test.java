/**
 * 【功能说明】
 * 本文件演示了Java中同一类的不同对象之间如何访问对方的私有成员。
 * Alpha类中有一个isEqualTo方法，该方法接收另一个Alpha对象作为参数，
 * 并在方法内部直接访问参数对象的私有成员变量iamprivate进行比较。
 * 这说明了Java的访问控制是在类级别（class-level）而非对象级别（object-level）的——
 * 同一个类的不同对象之间可以互相访问对方的私有成员。
 *
 * 【知识点】
 * 1. 类级别访问控制：Java中访问权限是在类级别控制的，同一个类中
 *    的所有方法（即使通过不同对象调用）都可以访问该类任何对象的私有成员
 * 2. 私有成员的作用域：private成员在所属类的所有方法中均可访问，
 *    包括访问其他同类型对象的私有成员
 * 3. this关键字：this表示当前对象，用于与参数对象的成员进行比较
 * 4. 对象比较：通过比较两个对象的内部状态（成员变量值）来判断是否相等
 * 5. 条件判断：if-else语句用于根据比较结果执行不同的代码分支
 * 6. 构造方法初始化：通过带参构造方法初始化私有成员变量
 */
package chp4_oo.exp4_10;                    // 声明包路径，该类属于chp4_oo.exp4_10包

/**
 * Alpha类：用于演示同类对象之间访问私有成员
 * 包含一个私有成员变量和比较方法
 */
class Alpha {                                // 定义一个名为Alpha的类（默认访问权限）
    private int iamprivate;                  // 私有成员变量iamprivate，只能在Alpha类内部访问

    /**
     * Alpha类的构造方法
     * @param i 用于初始化iamprivate的值
     */
    public Alpha(int i) {                    // 带参构造方法，接收一个int参数
        iamprivate = i;                      // 将参数i的值赋给私有成员变量iamprivate
    }

    /**
     * isEqualTo方法：比较当前对象与另一个Alpha对象是否相等
     * 在本类内部可以直接访问参数anotherAlpha的私有成员iamprivate
     * 因为访问权限是在类级别控制的（而不是对象级别）
     * @param anotherAlpha 另一个Alpha对象
     * @return 如果两个对象的iamprivate值相等返回true，否则返回false
     */
    boolean isEqualTo(Alpha anotherAlpha) {  // 方法，参数为另一个Alpha对象引用
        // 直接访问当前对象的私有成员this.iamprivate
        // 和参数对象的私有成员anotherAlpha.iamprivate
        if (this.iamprivate == anotherAlpha.iamprivate) { // 比较两个对象的私有成员变量值
            return true;                     // 如果相等，返回true
        } else {                             // 如果不相等
            return false;                    // 返回false
        }
    }
}

/**
 * Test类：包含main方法的主类
 * 创建两个Alpha对象并测试isEqualTo方法
 */
public class Test {                          // 定义一个名为Test的公共类

    /**
     * main方法：Java程序入口点
     * 创建两个Alpha对象，使用isEqualTo比较它们，输出比较结果
     * @param args 命令行参数数组
     */
    public static void main(String args[]) { // 主方法，JVM自动调用
        // 创建第一个Alpha对象aa，私有成员iamprivate被初始化为10
        Alpha aa = new Alpha(10);

        // 创建第二个Alpha对象bb，私有成员iamprivate被初始化为12
        Alpha bb = new Alpha(12);

        // 调用aa的isEqualTo方法，传入bb作为参数，比较aa和bb的私有成员是否相等
        if (aa.isEqualTo(bb)) {              // 调用aa对象的isEqualTo方法，将bb作为参数传入
            // isEqualTo方法内部：比较aa.iamprivate(10)与bb.iamprivate(12)
            // 10 != 12，所以返回false
            System.out.println("equal ");    // 如果返回true，输出"equal "
        } else {                             // 如果返回false
            System.out.println("not equal ");// 输出"not equal "
        }                                    // 程序输出：not equal
    }
}
