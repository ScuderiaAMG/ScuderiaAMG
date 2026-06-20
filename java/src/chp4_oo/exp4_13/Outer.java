/**
 * 【功能说明】
 * 本文件演示了Java中的局部内部类（Local Inner Class）。
 * 在方法makeInner()内部定义了一个名为Inner的局部内部类，
 * 该内部类可以访问外部类的成员变量（size），
 * 也可以访问方法中被声明为final的局部参数（finalLocalVar），
 * 但不能访问非final的局部变量（localVar）。
 * 该示例展示了局部内部类的定义、作用域限制以及对外部类成员的访问权限。
 *
 * 【知识点】
 * 1. 局部内部类（Local Inner Class）—— 定义在方法体内部的类
 * 2. 局部内部类只能访问被声明为final的局部变量和方法参数（Java 8+中为" effectively final"）
 * 3. 局部内部类可以无条件访问外部类的所有成员（包括私有成员）
 * 4. 局部内部类的作用域限定在定义它的方法体内
 * 5. 方法可以返回局部内部类创建的对象的引用（通过父类或接口引用返回）
 */
package chp4_oo.exp4_13;  // 包声明，表明当前类位于chp4_oo.exp4_13包中

/**
 * Outer类——外部类，包含一个局部内部类的演示
 */
class Outer{
    // 外部类的私有成员变量，size初始值为5
    private int size=5;

    /**
     * makeInner()方法，用于创建并返回一个局部内部类的实例
     * @param finalLocalVar 被声明为final的局部参数，局部内部类可以访问它
     * @return 返回一个Object类型的引用，实际指向Inner类的实例
     */
    public Object makeInner(final int finalLocalVar){
        // 非final的局部变量，局部内部类不能访问它（编译错误）
        int localVar=6;

        // 定义局部内部类Inner，作用域仅在makeInner()方法体内
        class Inner{
            /**
             * 重写Object类的toString()方法
             * @return 返回描述该内部类实例的字符串
             */
            public String toString(){
                // 可以访问外部类的私有成员size
                return ("#<Inner size="+size+
                //" localVar=" + localVar + //此处置局部变量localVar的访问非法
                // 上一行被注释的代码试图访问非final的局部变量localVar，会导致编译错误
                // 可以访问被声明为final的局部参数finalLocalVar
                " finalLocalVar="+finalLocalVar+">");
            }
        }
        return new Inner(); //在makeInner()方法中创建一个局部内部类的实例并返回
    }

    /**
     * 主方法，程序的入口
     * @param args 命令行参数数组
     */
    public static void main(String[] args){
        Outer outer=new Outer ();   // 创建外部类Outer的实例
        Object obj=outer.makeInner(40); // 调用makeInner()方法，传入40作为finalLocalVar的值
        System.out.println("The object is "+obj.toString());  // 打印obj的toString()返回结果
    }
}
