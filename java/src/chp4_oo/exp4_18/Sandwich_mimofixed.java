/**
 * 【功能说明】
 * 本文件演示了Java中复杂的继承层次结构和对象初始化顺序。
 * 通过一个"三明治"（Sandwich）的继承链展示了多层继承：
 * Meal -> Lunch -> PortableLunch -> Sandwich
 * 同时演示了组合（Composition）：Sandwich类中包含Bread、Cheese、Lettuce对象。
 * 运行main方法可以清晰地观察到：
 *   1. 继承链上各层父类的构造方法调用顺序（从顶层父类开始）
 *   2. 静态初始化块的执行顺序（在类加载时执行，且只执行一次）
 *   3. 成员变量的初始化与构造方法执行的先后关系
 *   4. 静态语句中创建对象导致的递归初始化现象
 *
 * 【知识点】
 * 1. 多层继承（Multilevel Inheritance）—— 继承链的层层传递
 * 2. 继承层次中的构造方法调用顺序：从最顶层的父类开始，逐层向下
 * 3. 静态初始化块（static block）—— 在类加载时执行，且仅执行一次
 * 4. 组合（Composition） vs 继承（Inheritance）
 * 5. 对象初始化顺序：静态变量/静态块（按声明顺序）-> 父类构造方法
 *    -> 成员变量初始化 -> 自身构造方法
 * 6. 在一个类的静态块中创建该类的实例会导致递归调用，理解其执行流程
 */
package chp4_oo.exp4_18;  // 包声明，表明当前类位于chp4_oo.exp4_18包中

/**
 * Meal类——继承链中的顶层基类（食物类）
 */
class Meal {
    // 静态成员变量，初始值为10
    static int i=10;

    // 静态初始化块，在类加载时执行，只执行一次
    static {
        // 先对i进行自增（i变为11），然后打印i的值
        System.out.println(++i);  // 输出结果：11
    }

    /**
     * Meal类的无参构造方法
     */
    Meal() {
        System.out.println("Meal()");  // 打印"Meal()"表示Meal构造方法被调用
    }
}

/**
 * Bread类——面包类，用于展示组合关系（Sandwich中包含Bread对象）
 */
class Bread {
    /**
     * Bread类的无参构造方法
     */
    Bread() {
        System.out.println("Bread()");  // 打印"Bread()"表示Bread构造方法被调用
    }
}

/**
 * Cheese类——奶酪类，用于展示组合关系（Sandwich中包含Cheese对象）
 */
class Cheese {
    /**
     * Cheese类的无参构造方法
     */
    Cheese() {
        System.out.println("Cheese()");  // 打印"Cheese()"表示Cheese构造方法被调用
    }
}

/**
 * Lettuce类——生菜类，用于展示组合关系（Sandwich中包含Lettuce对象）
 */
class Lettuce {
    /**
     * Lettuce类的无参构造方法
     */
    Lettuce() {
        System.out.println("Lettuce()");  // 打印"Lettuce()"表示Lettuce构造方法被调用
    }
}

/**
 * Lunch类——午餐类，继承自Meal，是继承链的第二层
 */
class Lunch extends Meal {
    /**
     * Lunch类的无参构造方法
     * 构造方法执行前会先调用父类Meal的构造方法
     */
    Lunch() {
        System.out.println("Lunch()");  // 打印"Lunch()"表示Lunch构造方法被调用
    }
}

/**
 * PortableLunch类——便携午餐类，继承自Lunch，是继承链的第三层
 */
class PortableLunch extends Lunch {
    /**
     * PortableLunch类的无参构造方法
     * 构造方法执行前会先调用父类Lunch的构造方法（Lunch又会先调用Meal的构造方法）
     */
    PortableLunch() {
        System.out.println("PortableLunch()");  // 打印"PortableLunch()"表示PortableLunch构造方法被调用
    }
}

/**
 * Sandwich类——三明治类，继承自PortableLunch，是继承链的最底层
 * 同时通过成员变量组合了Bread、Cheese、Lettuce对象
 */
public class Sandwich_mimofixed extends PortableLunch {
    // 组合对象：面包（成员变量初始化在构造方法之前执行）
    private Bread b = new Bread();
    // 组合对象：奶酪（成员变量初始化在构造方法之前执行）
    private Cheese c = new Cheese();
    // 组合对象：生菜（成员变量初始化在构造方法之前执行）
    private Lettuce l = new Lettuce();

    /**
     * Sandwich类的无参构造方法
     */
    public Sandwich_mimofixed() {
        System.out.println("Sandwich()");  // 打印"Sandwich()"表示Sandwich构造方法被调用
    }

    // 静态初始化块，在类加载时执行
    static {
        System.out.println("Static statement");  // 打印"Static statement"
        new Sandwich_mimofixed();  // 在静态块中创建Sandwich实例，会导致递归初始化
        // 注意：由于静态块只执行一次，此处的new Sandwich()不会再次触发静态块
        // 但会导致构造方法链的完整执行
    }

    /**
     * 主方法，程序的入口
     * @param args 命令行参数数组
     */
    public static void main(String[] args) {
        new Sandwich_mimofixed();  // 创建一个新的Sandwich对象，触发完整的初始化过程
    }
}
