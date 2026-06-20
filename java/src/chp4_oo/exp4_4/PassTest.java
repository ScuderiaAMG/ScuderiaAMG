/**
 * 【功能说明】
 * 本文件演示了Java中方法的参数传递机制——值传递（Pass by Value）。
 * 通过三种不同类型的参数（基本类型、String类型、引用类型）来展示：
 * - 基本类型作为参数时，方法内修改不会影响原变量
 * - String类型作为参数时（不可变对象），方法内重新赋值不影响原变量
 * - 引用类型作为参数时，方法内可以修改对象内部状态（成员变量）
 * 从而说明Java只有值传递，没有引用传递。
 *
 * 【知识点】
 * 1. Java参数传递机制：Java中所有参数传递都是值传递
 * 2. 基本类型参数传递：传递的是值的副本，方法内修改不影响原变量
 * 3. 引用类型参数传递：传递的是引用的副本（即对象地址的拷贝），
 *    通过引用可以修改对象内部状态，但无法改变引用本身指向的对象
 * 4. String的特殊性：String是不可变对象（immutable），
 *    重新赋值会创建新对象，原引用不受影响
 * 5. 成员变量与局部变量的区别：ptValue是成员变量，val和str是局部变量
 */
package chp4_oo.exp4_4;                     // 声明包路径，该类属于chp4_oo.exp4_4包

/**
 * PassTest类：参数传递测试类
 * 演示Java中不同类型参数的传递机制
 */
public class PassTest {                      // 定义一个名为PassTest的公共类
    float ptValue;                           // 成员变量ptValue，浮点类型，默认访问权限

    /**
     * changeInt方法：尝试修改基本类型参数
     * 由于Java是值传递，此方法内的修改不会影响调用者传入的变量
     * @param value 基本类型int参数，传递的是值的副本
     */
    public void changeInt(int value) {       // 方法，参数value是基本类型int
        value = 55;                          // 将形参value修改为55，这只是修改了副本，不影响原变量
    }                                        // 方法结束，形参value销毁

    /**
     * changeStr方法：尝试修改String类型参数
     * String是不可变对象，重新赋值会创建新对象，原引用不受影响
     * @param value String类型参数，传递的是引用的副本
     */
    public void changeStr(String value) {    // 方法，参数value是String类型（引用类型）
        value = new String("different");     // 创建新的String对象，局部变量value指向新对象
        // 注意：这改变了形参value的指向（指向了新对象），但不影响调用者传入的str变量
    }                                        // 方法结束，形参value销毁

    /**
     * changeObjValue方法：修改引用类型参数指向的对象内部状态
     * 虽然不能改变引用本身，但可以通过引用修改对象的成员变量
     * @param ref PassTest类型参数，传递的是引用的副本
     */
    public void changeObjValue(PassTest ref) { // 方法，参数ref是PassTest引用类型
        ref.ptValue = 99.0f;                 // 通过引用ref修改其指向对象的成员变量ptValue
        // 注意：这里的ref和main中的pt指向同一个对象，所以修改会影响到原对象
    }                                        // 方法结束，形参ref销毁，但对象的成员变量值已被修改

    /**
     * main方法：Java程序入口点
     * 依次测试基本类型、String类型、引用类型的参数传递行为
     * @param args 命令行参数数组
     */
    public static void main(String args[]) { // 主方法，JVM自动调用
        String str;                          // 声明String类型局部变量str（未初始化）
        int val;                             // 声明int类型局部变量val（未初始化）

        // 创建PassTest对象实例pt
        PassTest pt = new PassTest();        // 使用new关键字创建PassTest对象

        // ========== 测试1：基本类型参数传递 ==========
        val = 11;                            // 给局部变量val赋值为11
        pt.changeInt(val);                   // 调用changeInt方法，将val的值（11）的副本传递给方法
        // 方法内部修改了形参value为55，但不会影响val
        System.out.println("Int value is: " + val);
        // 输出：Int value is: 11（val的值没有被改变，仍然是11）

        // ========== 测试2：String类型参数传递 ==========
        str = new String("Hello");           // 创建String对象"Hello"，str指向该对象
        pt.changeStr(str);                   // 调用changeStr方法，将str的引用副本传递给方法
        // 方法内部创建了新的String对象"different"，形参value指向新对象
        // 但main中的str仍然指向原来的"Hello"对象
        System.out.println("Str value is: " + str);
        // 输出：Str value is: Hello（str仍然指向原对象，没有被改变）

        // ========== 测试3：引用类型参数传递（修改对象内部状态） ==========
        pt.ptValue = 101.0f;                 // 设置pt对象的成员变量ptValue为101.0
        pt.changeObjValue(pt);               // 调用changeObjValue方法，将pt的引用副本传递给方法
        // 方法内部通过形参ref修改了ptValue为99.0
        // 由于ref和pt指向同一个PassTest对象，修改会反映到pt上
        System.out.println("Pt value is: " + pt.ptValue);
        // 输出：Pt value is: 99.0（pt的ptValue被方法修改为99.0）
    }
}
