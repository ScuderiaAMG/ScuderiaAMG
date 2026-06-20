/**
 * 【功能说明】
 * 本程序演示了Java泛型方法（Generic Method）的用法。
 * MyBox<T>泛型类中定义了一个泛型方法inspect<U>，它拥有独立于
 * 类泛型参数的类型参数U。inspect方法接收任何类型的参数，
 * 并在运行时通过反射获取其实际类型信息，展示了泛型方法
 * 和Java反射API（getClass().getName()）的结合使用。
 *
 * 【知识点】
 * 1. 泛型方法（Generic Method）：方法声明中拥有独立的类型参数<U>
 * 2. 泛型方法的类型参数在方法返回类型之前声明：public <U> void inspect(U u)
 * 3. 泛型方法的类型参数与类泛型参数相互独立，可以不同
 * 4. 反射API（Reflection）：getClass().getName()获取对象在运行时的实际类名
 * 5. 自动装箱：new Integer(10)手动创建Integer对象
 * 6. 自动装箱：泛型方法中传入的String、Double等都是对象类型
 * 7. 类型擦除（Type Erasure）：泛型信息在运行时被擦除，但反射仍可获取实际类型
 */
package chp5_advanced.exp5_11;                             // 声明包路径，该文件位于chp5_advanced.exp5_11包中

class MyBox<T> {                                           // 泛型类MyBox<T>：T是类级别的类型参数
    private T t;                                           // 私有成员变量t，类型为T（由类泛型参数指定）

    public void add(T t) {                                 // add方法：将元素放入盒子中，参数类型为T
        this.t = t;                                        // 将参数t赋值给当前对象的成员变量t
    }

    public T get() {                                       // get方法：从盒子中取出元素，返回类型为T
        return t;                                          // 返回成员变量t的值
    }

    public <U> void inspect(U u) {                         // 泛型方法<U>：拥有独立的类型参数U，与类的类型参数T无关
        System.out.println("  T: " + t.getClass().getName()); // 通过反射获取成员变量t的实际类型并输出（类型T的实际运行时类型）
        System.out.println("  U: " + u.getClass().getName()); // 通过反射获取参数u的实际类型并输出（类型U的实际运行时类型）
        System.out.println();                              // 输出空行（分隔输出内容）
    }
}

public class BoxTest {                                     // 主类（public），用于测试泛型方法和泛型类
    public static void main(String[] args) {               // 主方法：程序执行的入口点
        MyBox<Integer> integerBox = new MyBox<Integer>();  // 创建MyBox<Integer>对象：类型参数T被指定为Integer
        integerBox.add(new Integer(10));                   // 向盒子中添加Integer对象（值为10）
        System.out.println("The first inspection:");       // 输出提示信息："第一次检查："
        integerBox.inspect("some text");                   // 调用泛型方法inspect，传入String类型参数（U被推断为String）
        System.out.println("The second inspection:");      // 输出提示信息："第二次检查："
        integerBox.inspect(new Double(100.0));             // 调用泛型方法inspect，传入Double类型参数（U被推断为Double）
    }
}
