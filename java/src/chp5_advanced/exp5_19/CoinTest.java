/**
 * 【功能说明】
 * 本程序演示了枚举类型的进阶用法——带属性的枚举和switch语句对枚举的支持。
 * Coin枚举包含面值属性（value），每个常量在声明时传入对应的面值。
 * CoinColor枚举定义了硬币的颜色（铜、镍、银）。在main方法中，
 * 遍历Coin所有常量，输出其名称和面值，并通过switch语句
 * 根据不同的硬币类型输出对应的颜色。
 *
 * 【知识点】
 * 1. 带属性的枚举：枚举常量可以拥有私有的成员变量和构造方法
 * 2. 枚举构造方法：必须为private（默认也是private），在枚举常量声明时调用
 * 3. 枚举常量可以有方法：如value()方法返回枚举常量的属性值
 * 4. switch支持枚举：case语句直接使用枚举常量名（不加枚举类型前缀）
 * 5. 多个case共享代码块：DIME和QUARTER共用同一段代码
 * 6. 枚举的values()方法：返回所有枚举常量数组
 * 7. 枚举常量自动拥有name()和toString()方法（toString()返回常量名）
 * 8. 枚举是一种特殊的类，可以实现接口、拥有方法和字段
 */
package chp5_advanced.exp5_19;                             // 声明包路径，该文件位于chp5_advanced.exp5_19包中

enum Coin {                                                // 定义Coin（硬币）枚举类型，带面值属性
    PENNY(1),                                              // 枚举常量：1分硬币，面值为1
    NICKEL(5),                                             // 枚举常量：5分硬币，面值为5
    DIME(10),                                              // 枚举常量：10分硬币，面值为10
    QUARTER(25);                                           // 枚举常量：25分硬币，面值为25

    private final int value;                               // 私有的final成员变量：硬币的面值（一旦赋值不可修改）

    Coin(int value) {                                      // 枚举构造方法：在声明枚举常量时调用，权限为默认（private）
        this.value = value;                                // 将构造参数赋值给成员变量value
    }

    public int value() {                                   // 公有方法：返回硬币的面值
        return value;                                      // 返回成员变量value
    }
}

enum CoinColor {                                           // 定义CoinColor（硬币颜色）枚举类型
    COPPER,                                                // 铜色
    NICKEL,                                                // 镍色
    SILVER                                                 // 银色
}

public class CoinTest {                                    // 主类（public），测试枚举类型
    public static void main(String[] args) {               // 主方法：程序执行的入口点
        for (Coin c : Coin.values()) {                     // 使用增强for-each循环遍历Coin枚举的所有常量
            System.out.print(c + ": " + c.value() + ", "); // 输出硬币名称（自动调用toString()）和面值
            switch (c) {                                   // switch语句根据枚举常量进行分支选择
                case PENNY:                                // 如果当前硬币是PENNY（1分）
                    System.out.println(CoinColor.COPPER);  // 输出颜色为铜色（COPPER）
                    break;                                 // 跳出switch语句
                case NICKEL:                               // 如果当前硬币是NICKEL（5分）
                    System.out.println(CoinColor.NICKEL);  // 输出颜色为镍色（NICKEL）
                    break;                                 // 跳出switch语句
                case DIME:                                 // 如果当前硬币是DIME（10分）
                case QUARTER:                              // 或者QUARTER（25分）（多个case共享代码块）
                    System.out.println(CoinColor.SILVER);  // 输出颜色为银色（SILVER）
                    break;                                 // 跳出switch语句
            }
        }
    }
}
