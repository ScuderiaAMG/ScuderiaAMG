/**
 * 【功能说明】
 * 本程序演示了Java泛型类（Generic Class）的定义和使用。
 * MyBox<T>是一个泛型容器类，类型参数T表示它可以存放任意类型的对象。
 * 在main方法中，使用MyBox<Integer>实例化一个专门存放Integer类型的盒子，
 * 并演示了添加元素和获取元素的操作，无需强制类型转换。
 *
 * 【知识点】
 * 1. 泛型类（Generic Class）：在类声明中使用类型参数<T>，使类可以处理多种类型
 * 2. 类型参数命名惯例：通常使用单个大写字母，如T（Type）、E（Element）、K（Key）、V（Value）
 * 3. 类型安全：通过泛型约束，MyBox<Integer>只能存放Integer类型对象
 * 4. 自动装箱（Auto-boxing）：aBox.add(1000)中int自动转换为Integer
 * 5. 自动拆箱（Auto-unboxing）：从MyBox中取出Integer自动转换为基本类型（如需）
 * 6. 简洁性与安全性：无需手动强制类型转换，避免了ClassCastException
 */
package chp5_advanced.exp5_9;                              // 声明包路径，该文件位于chp5_advanced.exp5_9包中

class MyBox<T> {                                           // 泛型类MyBox<T>：T是类型参数，表示盒子中存放的元素的类型
    private T t;                                           // 私有成员变量t，类型为T（由类型参数决定）

    public void add(T t) {                                 // add方法：将元素放入盒子中，参数类型为T
        this.t = t;                                        // 将参数t赋值给当前对象的成员变量t（this用于区分成员变量和参数）
    }

    public T get() {                                       // get方法：从盒子中取出元素，返回类型为T
        return t;                                          // 返回成员变量t的值
    }
}

public class MyBoxTest {                                   // 主类（public），用于测试泛型类MyBox
    public static void main(String args[]) {               // 主方法：程序执行的入口点
        MyBox<Integer> aBox;                               // 声明一个类型参数为Integer的MyBox引用变量aBox
        aBox = new MyBox<Integer>();                       // 创建MyBox<Integer>类型的对象并赋值给aBox（类型参数指定为Integer）
        aBox.add(1000);                                    // 向盒子中添加整数1000（自动装箱：int转为Integer）
        Integer i = aBox.get();                            // 从盒子中取出元素，自动获得Integer类型，无需强制转换
        System.out.println("The Integer is : " + i);       // 输出盒子中的Integer值："The Integer is : 1000"
    }
}
