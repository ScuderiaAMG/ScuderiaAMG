/**
 * 【功能说明】
 * 本文件演示了Java中可变参数（Varargs）的用法。
 * 定义了一个Calculation类，其中的avg方法使用可变参数(int... nums)，
 * 可以接受任意数量的int类型参数，计算并返回这些参数的平均值。
 * 在main方法中，分别传入3个参数和6个参数来调用avg方法，体现可变参数的灵活性。
 *
 * 【知识点】
 * 1. 可变参数（Varargs）：在类型后加三个点"..."表示可以接受零个或多个该类型的参数
 * 2. 可变参数的本质：在方法内部被当作数组处理
 * 3. 增强型for循环（foreach循环）：用于遍历数组或集合中的元素
 * 4. 类型转换（Casting）：将int类型转换为float类型，避免整数除法导致精度丢失
 * 5. 数组的length属性：获取数组的长度（元素个数）
 * 6. 可变参数的语法限制：可变参数必须是方法参数列表中的最后一个参数
 */
package chp4_oo.exp4_5;                     // 声明包路径，该类属于chp4_oo.exp4_5包

/**
 * Calculation类：计算类
 * 演示可变参数的使用——计算任意数量整数的平均值
 */
public class Calculation {                   // 定义一个名为Calculation的公共类

    /**
     * avg方法：计算平均值
     * 使用可变参数int... nums，可以传入任意数量的int参数
     * 方法内部将可变参数当作数组处理
     * @param nums 可变参数，表示要计算平均值的一系列整数
     * @return 所有参数的平均值（float类型）
     */
    public float avg(int... nums) {          // 定义avg方法，参数为int类型的可变参数（可传零到多个int值）
        int sum = 0;                         // 声明局部变量sum用于累加求和，初始值为0
        for (int x : nums) {                 // 增强型for循环（foreach），遍历nums数组中的每个元素
            sum += x;                        // 将当前元素x的值累加到sum中
        }                                    // 循环结束，sum中保存了所有参数的总和
        // 将int类型的sum强制转换为float，再进行除法运算，以避免整数除法截断
        return ((float) sum) / nums.length;  // 返回总和除以参数个数（数组长度），得到平均值
    }

    /**
     * main方法：Java程序入口点
     * 创建Calculation对象，使用不同数量的参数调用avg方法
     * @param args 命令行参数数组
     */
    public static void main(String args[]) { // 主方法，JVM自动调用
        Calculation cal = new Calculation(); // 创建Calculation类的对象实例cal

        // 调用avg方法，传入3个参数：10, 20, 30
        float average1 = cal.avg(10, 20, 30);
        // avg方法内部：sum=10+20+30=60，nums.length=3，返回60.0/3=20.0

        // 调用avg方法，传入6个参数：5, 6, 7, 8, 9, 10
        float average2 = cal.avg(5, 6, 7, 8, 9, 10);
        // avg方法内部：sum=5+6+7+8+9+10=45，nums.length=6，返回45.0/6=7.5

        // 输出第一次计算的平均值结果
        System.out.println("The average of 10,20,30 is" + " " + average1);
        // 输出：The average of 10,20,30 is 20.0

        // 输出第二次计算的平均值结果
        System.out.println("The average of 5, 6, 7, 8, 9, 10 is" + " " + average2);
        // 输出：The average of 5, 6, 7, 8, 9, 10 is 7.5
    }
}
