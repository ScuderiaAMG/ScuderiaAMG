/*
 * ============================================================
 * 【功能说明】
 * 本程序演示了如何自定义异常类以及如何抛出自定义异常。
 * MyException 类继承自 Exception，提供了无参和有参两个构造方法，
 * 有参构造方法通过 super(msg) 将异常消息传递给父类。
 * UsingMyException 类的 f() 和 g() 方法分别演示了：
 * - f() 使用无参构造方法抛出自定义异常
 * - g() 使用有参构造方法抛出带消息的自定义异常
 * TestMyException 主类分别调用这两个方法并用 catch 捕获
 * 自定义异常，通过 e.printStackTrace() 打印完整的异常堆栈跟踪。
 *
 * 【知识点】
 * 1. 自定义异常类：继承 Exception（已检查异常）或 RuntimeException
 * 2. super(msg) 调用父类构造方法设置异常消息
 * 3. throw 关键字：手动抛出异常对象
 * 4. throws 关键字：声明方法可能抛出的异常
 * 5. 无参构造与有参构造方法的重载
 * 6. e.printStackTrace()：打印异常发生时的调用堆栈信息
 *    ——包含异常类型、消息和完整的调用链
 * 7. 异常对象的创建与传播流程
 * ============================================================
 */
package chp6_exception.exp6_6;                             // 声明包路径，属于第6章异常处理实验6

// 自定义异常类MyException，继承自Exception，成为已检查异常
class MyException extends Exception {                      // 定义MyException类，继承Exception类
    MyException() {                                        // 无参构造方法：创建不含详细消息的异常对象
    }                                                      // 无参构造方法结束

    MyException(String msg) {                              // 有参构造方法：接收一个字符串参数作为异常消息
        super(msg);                                        // 调用父类Exception的构造方法，设置异常详细消息
    }                                                      // 有参构造方法结束
}                                                          // MyException类结束

// 使用自定义异常的类
class UsingMyException {                                   // 定义UsingMyException类
    void f() throws MyException {                          // 方法f()声明抛出MyException（通过throws将异常传递给调用者）
        System.out.println("Throws MyException from f()"); // 打印提示信息，表示即将从f()抛出MyException
        throw new MyException();                           // 使用无参构造创建MyException实例并抛出（无详细消息）
    }                                                      // f()方法结束

    void g() throws MyException {                          // 方法g()声明抛出MyException
        System.out.println("Throws MyException from g()"); // 打印提示信息，表示即将从g()抛出MyException
        throw new MyException("Originated in g()");        // 使用有参构造创建MyException实例并抛出（带详细消息"Originated in g()"）
    }                                                      // g()方法结束
}                                                          // UsingMyException类结束

public class TestMyException {                             // 公开测试类TestMyException
    public static void main(String args[]) {               // 程序入口点
        UsingMyException m = new UsingMyException();       // 创建UsingMyException实例

        try {                                              // try块开始：调用可能抛出MyException的f()方法
            m.f();                                         // 调用f()方法，该方法内部抛出无参MyException
        } catch (MyException e) {                          // 捕获MyException类型的异常
            e.printStackTrace();                           // 打印异常堆栈跟踪信息（异常类型、消息、调用链）
        }                                                  // catch块结束

        try {                                              // try块开始：调用可能抛出MyException的g()方法
            m.g();                                         // 调用g()方法，该方法内部抛出带消息的MyException
        } catch (MyException e) {                          // 捕获MyException类型的异常
            e.printStackTrace();                           // 打印异常堆栈跟踪信息（包含"Originated in g()"消息）
        }                                                  // catch块结束
    }                                                      // main方法结束
}                                                          // 类定义结束
