/**
 * 【功能说明】
 * 本程序演示了Java泛型（Generics）在集合类中的使用。
 * 与exp5_7相比，本程序使用泛型参数List<Integer>明确指定了
 * 集合只能存放Integer类型的对象。如果试图添加其他类型（如String），
 * 编译期就会报错，提供了类型安全性。同时，从集合中取出元素时
 * 无需手动强制类型转换。
 *
 * 【知识点】
 * 1. 泛型（Generics）：JDK 5引入的类型参数化机制
 * 2. 类型参数语法：List<Integer>表示"元素类型为Integer的列表"
 * 3. 编译期类型检查：泛型将类型检查提前到编译阶段，避免运行时ClassCastException
 * 4. 自动类型推断：从泛型集合中取出元素时自动获得正确的类型，无需强制转换
 * 5. 菱形运算符（Diamond Operator）：new LinkedList<>()中<>可省略类型参数（JDK 7+）
 * 6. 编译错误vs运行时异常：泛型帮助在编译期发现类型不匹配问题
 * 7. 简化的自动装箱：listofInteger.add(8)可自动装箱为Integer（已注释）
 */
package chp5_advanced.exp5_8;                              // 声明包路径，该文件位于chp5_advanced.exp5_8包中

import java.util.LinkedList;                               // 导入LinkedList类，用于创建链表集合
import java.util.List;                                     // 导入List接口，作为集合的引用类型

public class ListTestWithGenerics {                        // 主类（public），演示使用泛型的集合
    public static void main(String[] args) {               // 主方法：程序执行的入口点
        List<Integer> listofInteger = new LinkedList<Integer>(); // 使用泛型参数<Integer>创建LinkedList，只能存放Integer类型对象
        listofInteger.add(new Integer(2000));              // 向集合中添加Integer对象（值为2000），符合泛型约束
        listofInteger.add("8");                            // 编译错误！试图添加String对象"8"，泛型在编译期阻止此操作
        // listofInteger.add(new Integer(8));              // （已注释）正确的添加方式：添加Integer对象
        // listofInteger.add(8);                           // （已注释）更简洁的方式：JDK 5自动装箱，int自动转换为Integer
        Integer x = listofInteger.get(0);                  // 从集合中获取元素，自动返回Integer类型，无需强制类型转换
        System.out.println(x);                             // 输出整数x的值
        x = listofInteger.get(1);                          // 从集合中获取索引1处的元素，同样自动返回Integer类型
        System.out.println(x);                             // 输出整数x的值
    }
}
