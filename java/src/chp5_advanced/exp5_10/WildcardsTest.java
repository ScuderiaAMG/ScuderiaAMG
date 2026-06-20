/**
 * 【功能说明】
 * 本程序演示了Java泛型中的通配符（Wildcards，即?）的使用，
 * 特别是上界通配符（Upper Bounded Wildcards）"? extends Animal"。
 * 定义了Animal类及其子类Lion和ButterFly，以及Cage<E>泛型笼子类。
 * feedAnimals方法接受Cage<? extends Animal>类型的参数，
 * 意味着可以传入任何存放Animal或其子类的笼子，实现了更灵活的参数类型匹配。
 *
 * 【知识点】
 * 1. 泛型通配符?：表示未知类型，用于方法参数的类型匹配
 * 2. 上界通配符 ? extends T：表示类型可以是T或T的任何子类
 * 3. 泛型类的继承/扩展：Cage<E> extends LinkedList<E>，继承了LinkedList的所有功能
 * 4. 增强型for循环（for-each）：for (Animal a : someCage) 简化集合遍历
 * 5. 继承体系中的多态：Animal、Lion、ButterFly构成继承层次结构
 * 6. 泛型与多态的结合：通配符使得可以编写处理多种泛型类型的通用方法
 * 7. 协变（Covariance）：Cage<Lion>是Cage<? extends Animal>的子类型
 */
package chp5_advanced.exp5_10;                             // 声明包路径，该文件位于chp5_advanced.exp5_10包中

import java.util.LinkedList;                               // 导入LinkedList类，用于被Cage类继承

class Cage<E> extends LinkedList<E> {                      // 泛型类Cage<E>：继承LinkedList<E>，表示一个可以存放E类型动物的笼子
}                                                          // 类体为空，继承了LinkedList的所有方法（add、get、迭代等）

class Animal {                                             // Animal（动物）基类
    public void feedMe() {                                 // feedMe方法：喂食动物（基类中为空实现）
    }                                                      // 方法体为空，由子类覆盖提供具体实现
}

class Lion extends Animal {                                // Lion（狮子）类，继承自Animal
    public void feedMe() {                                 // 覆盖（Override）基类的feedMe方法
        System.out.println("Feeding lions");               // 输出"正在喂狮子"
    }
}

class ButterFly extends Animal {                           // ButterFly（蝴蝶）类，继承自Animal
    public void feedMe() {                                 // 覆盖（Override）基类的feedMe方法
        System.out.println("Feeding butterflies");         // 输出"正在喂蝴蝶"
    }
}

public class WildcardsTest {                               // 主类（public），演示通配符的用法
    public static void main(String args[]) {               // 主方法：程序执行的入口点
        WildcardsTest t = new WildcardsTest();             // 创建WildcardsTest对象（用于调用非静态方法feedAnimals）
        Cage<Lion> lionCage = new Cage<Lion>();            // 创建专门存放Lion对象的笼子（泛型参数为Lion）
        Cage<ButterFly> butterflyCage = new Cage<ButterFly>(); // 创建专门存放ButterFly对象的笼子（泛型参数为ButterFly）
        lionCage.add(new Lion());                          // 向lionCage中添加一个Lion对象
        butterflyCage.add(new ButterFly());                // 向butterflyCage中添加一个ButterFly对象
        t.feedAnimals(lionCage);                           // 调用feedAnimals方法传入lionCage（Cage<Lion>匹配? extends Animal）
        t.feedAnimals(butterflyCage);                      // 调用feedAnimals方法传入butterflyCage（Cage<ButterFly>匹配? extends Animal）
    }

    void feedAnimals(Cage<? extends Animal> someCage) {    // 方法参数使用上界通配符：可以接受存放任何Animal子类的笼子
        for (Animal a : someCage) {                        // 使用增强型for循环遍历笼子中的所有动物
            a.feedMe();                                    // 多态调用：根据实际对象类型调用对应的feedMe方法
        }
    }
}
